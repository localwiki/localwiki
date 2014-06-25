import copy

from django.conf import settings
from django.views.generic import TemplateView as DjangoTemplateView
from django.views.generic import View, ListView
from django.http import Http404, HttpResponseNotFound
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.http import HttpResponseForbidden, HttpResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from django.contrib.gis.geos import GEOSGeometry, Polygon, MultiPolygon
from django.template.loader import render_to_string
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy

from follow.utils import follow as do_follow
from actstream import action

from localwiki.utils.views import CreateObjectMixin, AuthenticationRequired
from localwiki.utils.urlresolvers import reverse

from .models import Region, RegionSettings, BannedFromRegion, slugify
from .forms import RegionForm, RegionSettingsForm, AdminSetForm, BannedSetForm


def region_404_response(request, slug):
    region_add = reverse('regions:add')
    msg = _('<p>Region "%s" not found. Would you like to <a href="%s" rel="nofollow">create it</a>?</p>' %
        (slug, region_add))
    html = render_to_string('404.html', {'message': msg}, RequestContext(request))
    return HttpResponseNotFound(html)


class RegionMixin(object):
    """
    Provides helpers to views that deal with Regions.
    """
    def get_region(self, request=None, kwargs=None):
        """
        Returns the Region associated with this view.
        """
        if kwargs is None:
            kwargs = self.kwargs
        if request is None:
            request = self.request

        if kwargs.get('region'):
            region_slug = kwargs.get('region')
            r = get_object_or_404(Region, slug=slugify(region_slug))
        else:
            rs = get_object_or_404(RegionSettings, domain=request.META['HTTP_HOST'])
            r = rs.region
        if not r.is_active:
            raise Http404(_("Region '%s' was deleted." % r.slug))
        return r

    def get_queryset(self):
        qs = super(RegionMixin, self).get_queryset()
        return qs.filter(region=self.get_region(), region__is_active=True)

    def get_context_data(self, *args, **kwargs):
        context = super(RegionMixin, self).get_context_data(*args, **kwargs)
        context['region'] = self.get_region()
        if hasattr(self, 'request'):
            context['is_region_admin'] = context['region'].is_admin(self.request.user)
        return context


class RegionAdminRequired(object):
    """
    Mixin to make a view only usable to a region's admins.
    """
    forbidden_message = ugettext_lazy('Sorry, you are not allowed to perform this action.')

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        region = self.get_region()

        if region.is_admin(self.request.user):
            return super(RegionAdminRequired, self).dispatch(request, *args, **kwargs)

        msg = self.forbidden_message
        html = render_to_string('403.html', {'message': msg}, RequestContext(request))
        return HttpResponseForbidden(html)


class TemplateView(RegionMixin, DjangoTemplateView):
    pass


class RegionListView(ListView):
    model = Region
    context_object_name = 'regions'
    zoom_to_data = True

    def get_queryset(self):
        return Region.objects.filter(is_active=True).exclude(regionsettings__is_meta_region=True).order_by('full_name')

    def get_context_data(self, *args, **kwargs):
        from maps.widgets import InfoMap

        def popup_html(obj):
            url = reverse('frontpage', kwargs={'region': obj.slug}) 
            return '<a href="%s">%s</a>' % (url, obj.full_name)

        context = super(RegionListView, self).get_context_data(*args, **kwargs)
        map_objects = [(obj.geom.centroid, popup_html(obj)) for obj in self.get_queryset() if obj.geom]

        olwidget_options = copy.deepcopy(getattr(settings,
            'OLWIDGET_DEFAULT_OPTIONS', {}))

        # Center to show most of the US'ish
        olwidget_options['default_lat'] = 39.79
        olwidget_options['default_lon'] = -100.99
        olwidget_options['zoomToDataExtent'] = self.zoom_to_data

        map_opts = olwidget_options.get('map_options', {})
        map_controls = map_opts.get('controls', [])
        if 'KeyboardDefaults' in map_controls:
            map_controls.remove('KeyboardDefaults')
        olwidget_options['map_options'] = map_opts
        olwidget_options['map_div_class'] = 'mapwidget small'
        context['map'] = InfoMap(
            map_objects,
            options=olwidget_options)

        return context


class MainPageView(View):
    def get(self, request):
        from activity.views import FollowedActivity

        if request.user.is_authenticated():
            view_func = FollowedActivity.as_view()
        else:
            view_func = SplashPageView.as_view()
        return view_func(request)


class SplashPageView(RegionListView):
    template_name = 'regions/main.html'
    zoom_to_data = False


class RegionCreateView(AuthenticationRequired, CreateView):
    model = Region
    form_class = RegionForm

    def get_forbidden_message(self):
        forbidden_message = _(
            'To create a region you must first <strong><a href="%(login_url)s?next=%(current_path)s">log in</a></strong> or '
            '<strong><a href="%(register_url)s?next=%(current_path)s">create an account</a></strong>.') % {
                'login_url': reverse('auth_login'),
                 'current_path': reverse('regions:add'),
                 'register_url': reverse('registration_register'),
        }
        return forbidden_message

    def get_success_url(self):
        msg = _(
            "You've created a new LocalWiki region! "
            "We've set you up as an admin for this region. "
            "Learn more about <a href=\"http://localwiki.net/main/Local_Adminship_Hub\" target=\"_blank\">LocalWiki adminship here</a>."
        )
        messages.add_message(self.request, messages.SUCCESS, msg)
        return reverse('frontpage', kwargs={'region': self.object.slug})

    def get_form_kwargs(self):
        kwargs = super(RegionCreateView, self).get_form_kwargs()
        kwargs['initial']['default_language'] = getattr(self.request,
            'LANGUAGE_CODE', settings.LANGUAGE_CODE)
        if kwargs.get('data'):
            kwargs['data'] = kwargs['data'].copy()  # otherwise immutable
            kwargs['data']['slug'] = slugify(kwargs['data']['slug'])
        return kwargs

    def form_invalid(self, form):
        geom = form.data.get('geom', None)
        if form.errors.get('geom'):
            form.errors['geom'][0] = _('There was a problem with the map area you drew. Please re-draw it and try again.')
            # Reset the geom so we don't get rendering issues.
            form.data['geom'] = ''
        response = super(RegionCreateView, self).form_invalid(form)
        return response


    def form_valid(self, form):
        response = super(RegionCreateView, self).form_valid(form)
        region = self.object

        # Set the language
        region.regionsettings.default_language = form.cleaned_data['default_language']
        region.regionsettings.save()

        # Create the initial pages, etc in the region.
        region.populate_region()

        # Add the creator as the initial region admin.
        if self.request.user.is_authenticated():
            region.regionsettings.admins.add(self.request.user)

        # Set the creator as following the region
        do_follow(self.request.user, region)

        # Notify followers that user created region
        action.send(self.request.user, verb='created region', action_object=region)

        return response


class RegionSettingsView(RegionAdminRequired, RegionMixin, FormView):
    template_name = 'regions/settings.html'
    form_class = RegionSettingsForm

    def get_initial(self):
        region = self.get_region()
        return {
            'full_name': region.full_name,
            'geom': region.geom,
            'default_language': region.regionsettings.default_language,
        }

    def form_valid(self, form):
        response = super(RegionSettingsView, self).form_valid(form)
        region = self.get_region()
        region.full_name = form.cleaned_data['full_name']
        if form.cleaned_data['default_language']:
            region.regionsettings.default_language = form.cleaned_data['default_language']
            region.regionsettings.save()

        poly = GEOSGeometry(form.cleaned_data['geom'])
        if isinstance(poly, Polygon):
            region.geom = MultiPolygon(poly)
        elif isinstance(poly, MultiPolygon):
            region.geom = poly

        region.save()
        messages.add_message(self.request, messages.SUCCESS, _("Settings updated!"))
        return response

    def get_success_url(self):
        return reverse('regions:settings', kwargs={'region': self.get_region().slug})

    def get_context_data(self, *args, **kwargs):
        context = super(RegionSettingsView, self).get_context_data(*args, **kwargs)
        region = self.get_region()
        if hasattr(region, 'bannedfromregion'):
            context['banned_users'] = region.bannedfromregion.users.all()
        else:
            context['banned_users'] = []
        return context


class RegionAdminsUpdate(RegionAdminRequired, RegionMixin, UpdateView):
    form_class = AdminSetForm
    model = RegionSettings
    template_name = 'regions/admins_update.html'

    def get_object(self):
        return self.get_region().regionsettings

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, _("Region admins updated!"))
        return reverse('regions:settings', kwargs={'region': self.get_region().slug})

    def get_form_kwargs(self):
        kwargs = super(RegionAdminsUpdate, self).get_form_kwargs()
        # We need to pass the `region` to the AdminSetForm
        kwargs['region'] = self.get_region()
        kwargs['this_user'] = self.request.user
        return kwargs


class RegionBannedUpdate(RegionAdminRequired, RegionMixin, UpdateView):
    form_class = BannedSetForm
    model = BannedFromRegion
    template_name = 'regions/banned_update.html'

    def get_object(self):
        banned, created = BannedFromRegion.objects.get_or_create(region=self.get_region())
        return banned

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, _("Banned users updated."))
        return reverse('regions:settings', kwargs={'region': self.get_region().slug})

    def get_form_kwargs(self):
        kwargs = super(RegionBannedUpdate, self).get_form_kwargs()
        # We need to pass the `region` to the BannedSetForm.
        kwargs['region'] = self.get_region()
        return kwargs


def suggest(request, *args, **kwargs):
    """
    Simple region suggest.
    """
    # XXX TODO: Break this out when doing the API work.
    from haystack.query import SearchQuerySet 
    import json

    term = request.GET.get('term', None)
    if not term:
        return HttpResponse('')
    results = SearchQuerySet().models(Region).filter(name_auto=term).filter_or(slug_auto=term)
    # Set a sane limit
    results = results[:20]

    results = [{'value': p.full_name, 'url': p.object.get_absolute_url(), 'slug': p.object.slug} for p in results]
    return HttpResponse(json.dumps(results))
