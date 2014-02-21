from django.contrib.auth.models import User
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.views.generic.edit import UpdateView, FormView
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.views.generic import RedirectView

from guardian.shortcuts import get_users_with_perms, assign_perm, remove_perm

from regions.models import Region
from regions import get_main_region
from regions.views import RegionMixin, RegionAdminRequired
from pages.models import Page

from .models import UserProfile
from .forms import UserSetForm, UserSettingsForm


class UserPageView(RedirectView):
    permanent = False
    query_string = True

    def get_redirect_url(self, **kwargs):
        username = self.kwargs.get('username')
        user = User.objects.get(username=username)
        pagename = "Users/%s" % username
        user_pages = Page.objects.filter(name=pagename)
        if user_pages:
            # Has a userpage in a region
            user_page = user_pages[0]
        else:
            # Check to see if they've edited a region recently
            edited_pages = Page.versions.filter(version_info__user=user)
            if edited_pages:
                region = edited_pages[0].region
                user_page = Page(name=pagename, region=region)
            else:
                user_page = Page(name=pagename, region=get_main_region())
        return user_page.get_absolute_url()


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
