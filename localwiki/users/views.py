from urlparse import urlparse

from django.contrib.auth.models import User
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth import logout
from django.core.exceptions import PermissionDenied
from django.template.loader import render_to_string
from django.views.generic.edit import UpdateView, FormView
from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView, TemplateView
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.db.models import Count
from django.contrib.auth.models import User

from guardian.shortcuts import get_users_with_perms, assign_perm, remove_perm
from follow.models import Follow

from versionutils.versioning.utils import is_versioned
from regions.models import Region
from regions import get_main_region
from regions.views import RegionMixin, RegionAdminRequired

from .templatetags.user_tags import user_link
from .models import UserProfile
from .forms import UserSetForm, UserSettingsForm, DeactivateForm


def humanize_int(n):
    mag = 0
    if n < 1000:
        return str(n)
    while n>= 1000:
        mag += 1
        n /= 1000.0
    return '%.1f%s' % (n, ['', 'k', 'M', 'B', 'T', 'P'][mag])


def pretty_url(url):
    if urlparse(url).path == '/':
        # Strip trailing slash
        url = url[:-1]
    if url.startswith('http://'):
        url = url[7:]
    elif url.startswith('https://'):
        url = url[8:]
    return url


def get_user_page(user, request):
    """
    Hacky heuristics for picking the underlying Page that holds the userpage content.

    TODO: Make this all belong the a single administrative region, 'users', once we 
          have a notifications framework in place.
    """
    from pages.models import Page, slugify

    pagename = "Users/%s" % user.username
    user_pages = Page.objects.filter(slug=slugify(pagename))
    if user_pages:
        # Just pick the first one
        return user_pages[0]
    else:
        # Check to see if they've edited a region recently
        edited_pages = Page.versions.filter(version_info__user=user)
        referer = request.META.get('HTTP_REFERER')
        if edited_pages:
            region = edited_pages[0].region
            return Page(name=pagename, region=region)
        # Let's try and guess by the previous URL. Ugh!
        if referer:
            urlparts = urlparse(referer)
            # Is this host us?
            for host in settings.ALLOWED_HOSTS:
                if urlparts.netloc.endswith(host):
                    pathparts = parts.path.split('/')
                    # Is the path in a region?
                    if len(pathparts) > 1 and Region.objects.filter(slug=pathparts[1]).exists():
                        return Page(name=pagename, region=Region.objects.get(slug=pathparts[1]))

        # Put it in the main region for now :/
        return Page(name=pagename, region=get_main_region())


class UserPageView(TemplateView):
    template_name = 'users/user_page.html'

    def get_context_data(self, **kwargs):
        from pages.models import Page, PageFile
        from maps.models import MapData
        from tags.models import PageTagSet

        context = super(UserPageView, self).get_context_data(**kwargs)

        username = self.kwargs.get('username')
        user = get_object_or_404(User, username__iexact=username)
        profile = getattr(user, 'userprofile', None)
        
        #########################
        # Calculate user stats
        #########################
        page_edits = Page.versions.filter(version_info__user=user).count()
        map_edits = MapData.versions.filter(version_info__user=user).count()
        tag_edits = PageTagSet.versions.filter(version_info__user=user).count()
        file_edits = PageFile.versions.filter(version_info__user=user).count()

        # Total contributions across data types
        num_contributions = page_edits + map_edits + tag_edits + file_edits

        # Total 'pages touched'
        num_pages_edited = Page.versions.filter(version_info__user=user).values('slug').distinct().count()

        # Total 'maps touched'
        num_maps_edited = MapData.versions.filter(version_info__user=user).values('page__slug').distinct().count()

        # Regions followed
        regions_followed = Follow.objects.filter(user=user).exclude(target_region=None)

        # Users, pages followed
        num_pages_followed = Follow.objects.filter(user=user).exclude(target_page=None).count()
        num_users_followed = Follow.objects.filter(user=user).exclude(target_user=None).exclude(target_user=user).count()

        context['user_for_page'] = user
        context['pretty_personal_url'] = pretty_url(user.userprofile.personal_url) if user.userprofile.personal_url else None
        context['page'] = get_user_page(user, self.request)
        context['num_contributions'] = humanize_int(num_contributions)
        context['num_pages_edited'] = humanize_int(num_pages_edited)
        context['num_maps_edited'] = humanize_int(num_maps_edited)
        context['regions_followed'] = regions_followed
        context['num_pages_followed'] = num_pages_followed
        context['num_users_followed'] = num_users_followed

        return context


class GlobalUserpageRedirectView(RedirectView):
    permanent = True

    def get_redirect_url(self, **kwargs):
        username = kwargs.get('username')
        return '/Users/%s' % username


class SetPermissionsView(RegionAdminRequired, RegionMixin, FormView):
    form_class = UserSetForm

    def get_initial(self):
        # Technically, this returns all users with *any* permissions
        # on the object, but for our purposes this is okay.
        users = get_users_with_perms(self.get_object())
        if users:
            everyone_or_user_set = 'just_these_users'
        else:
            everyone_or_user_set = 'everyone'
        return {'users': users, 'everyone_or_user_set': everyone_or_user_set}

    def get_object_type(self, obj):
        return obj.__class__.__name__.lower()

    def get_form_kwargs(self):
        kwargs = super(SetPermissionsView, self).get_form_kwargs()
        # We need to pass the `region` to the UserSetForm.
        kwargs['region'] = self.get_region()
        kwargs['this_user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super(SetPermissionsView, self).form_valid(form)

        obj = self.get_object()
        obj_type = self.get_object_type(obj)

        users_old = set(get_users_with_perms(self.get_object()))
        users = set(form.cleaned_data['users'])

        if form.cleaned_data['who_can_change'] == 'everyone':
            # Clear out all users
            del_users = users_old
            add_users = []
        else:
            del_users = users_old - users
            add_users = users - users_old

        for u in add_users:
            assign_perm('change_%s' % obj_type, u, obj)
            assign_perm('add_%s' % obj_type, u, obj)
            assign_perm('delete_%s' % obj_type, u, obj)

        for u in del_users:
            remove_perm('change_%s' % obj_type, u, obj)
            remove_perm('add_%s' % obj_type, u, obj)
            remove_perm('delete_%s' % obj_type, u, obj)

        messages.add_message(self.request, messages.SUCCESS, _("Permissions updated!"))
        return response


class UserSettingsView(UpdateView):
    template_name = 'users/settings.html'
    model = UserProfile
    form_class = UserSettingsForm

    def get_object(self):
        if not self.request.user.is_authenticated():
            raise PermissionDenied(_("You must be logged in to change user settings."))
        return UserProfile.objects.get(user=self.request.user)

    def form_valid(self, form):
        response = super(UserSettingsView, self).form_valid(form)

        userprofile = self.get_object()
        userprofile.user.email = form.cleaned_data['email']
        userprofile.user.name = form.cleaned_data['name']
        if form.cleaned_data['gravatar_email'] != userprofile.user.email:
            userprofile._gravatar_email = form.cleaned_data['gravatar_email']
        userprofile.user.save()
        userprofile.save()

        messages.add_message(self.request, messages.SUCCESS, _("User settings updated!"))
        return response

    def get_initial(self):
        initial = super(UserSettingsView, self).get_initial()

        initial['name'] = self.object.user.name
        initial['email'] = self.object.user.email
        initial['gravatar_email'] = self.object.gravatar_email
        return initial

    def get_success_url(self):
        return self.request.user.get_absolute_url()


class UserDeactivateView(FormView):
    template_name = 'users/deactivate.html'
    form_class = DeactivateForm 

    def get_context_data(self, **kwargs):
        if not self.request.user.is_authenticated():
            raise PermissionDenied(_("You must be logged in to change user settings."))
        return super(UserDeactivateView, self).get_context_data(**kwargs)

    def get_initial(self):
        return {}

    def form_valid(self, form):
        response = super(UserDeactivateView, self).form_valid(form)

        if not self.request.user.is_authenticated():
            raise PermissionDenied(_("You must be logged in to change user settings."))

        self.request.user.is_active = not form.cleaned_data['disabled']
        self.request.user.save()

        logout(self.request)
        messages.add_message(self.request, messages.SUCCESS, _("Your account has been de-activated."))

        return response

    def get_success_url(self):
        return '/'


class AddContributorsMixin(object):
    """
    Add the editors of this object to the view's context as
    `contributors_html` and `contributors_number`.
    """
    def get_context_data(self, **kwargs):
        context = super(AddContributorsMixin, self).get_context_data(**kwargs)
        obj = self.get_object()

        if not is_versioned(obj):
            return context

        users_by_edit_count = obj.versions.exclude(history_user__isnull=True).order_by('history_user').values('history_user').annotate(nedits=Count('history_user')).order_by('-nedits')
        top_3 = users_by_edit_count[:3]
        num_rest = len(users_by_edit_count[3:])

        top_3_html = ''
        for u_info in top_3:
            user = User.objects.get(pk=u_info['history_user'])
            top_3_html += user_link(user, region=self.get_region(), show_username=False, size=24)

        context['contributors_html'] = top_3_html
        context['contributors_number'] = num_rest
    
        return context


def suggest_users(request, region=None):
    """
    Simple users suggest.
    """
    # XXX TODO: Break this out when doing more API work.
    import json

    term = request.GET.get('term', None)
    if not term:
        return HttpResponse('')
    results = User.objects.filter(
        username__istartswith=term)
    results = [t.username for t in results]
    return HttpResponse(json.dumps(results))
