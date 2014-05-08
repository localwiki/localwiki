from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from versionutils.versioning.views import UpdateView
from versionutils import diff
from utils.views import CreateObjectMixin, PermissionRequiredMixin, DeleteView
from pages.models import Page, slugify
from regions.views import RegionMixin
from regions.models import Region
from users.views import SetPermissionsView

from models import Redirect
from forms import RedirectForm


class RedirectUpdateView(PermissionRequiredMixin, CreateObjectMixin,
        RegionMixin, UpdateView):
    model = Redirect
    form_class = RedirectForm

    def get_object(self):
        source = slugify(self.kwargs.get('slug'))
        redirect = Redirect.objects.filter(source=source, region=self.get_region())
        if redirect:
            return redirect[0]
        return Redirect(source=source, region=self.get_region())

    def get_context_data(self, **kwargs):
        context = super(RedirectUpdateView, self).get_context_data(**kwargs)
        p = Page.objects.filter(slug=self.object.source, region=self.get_region())
        if p:
            context['page'] = p[0]
        else:
            context['page'] = Page(slug=self.object.source,
                name=self.object.source, region=self.get_region())
        context['exists'] = Redirect.objects.filter(
            source=self.object.source, region=self.get_region()).exists()
        return context

    def get_form_kwargs(self):
        kwargs = super(RedirectUpdateView, self).get_form_kwargs()
        # We need to pass the `region` to the RedirectForm.
        kwargs['region'] = self.get_region()
        return kwargs

    def success_msg(self):
        # NOTE: This is eventually marked as safe when rendered in our
        # template.  So do *not* allow unescaped user input!
        return (
            '<div>' +\
            _('Thank you for your changes. ') +\
            _('This page now redirects to <a href="%(url)s">%(obj)s</a>.')  % {
               'url': self.object.destination.get_absolute_url(),
               'obj': self.object}  +\
            '</div>'
        )

    def get_success_url(self):
        return reverse('pages:show',
            args=[self.object.region.slug, self.object.source])

    def create_object(self):
        return Redirect(source=slugify(self.kwargs['slug']))

    def get_protected_objects(self):
        protected = []
        slug = slugify(self.kwargs['slug'])
        region = Region.objects.get(slug=self.kwargs['region'])

        page = Page.objects.filter(slug=slug, region=region)
        if page:
            protected.append(page[0])
        redirect = Redirect.objects.filter(source=slug, region=region)
        if redirect:
            protected.append(redirect[0])

        return protected

    def permission_for_object(self, obj):
        # We want to tie the redirect permissions to the Redirect object
        # -and- the Page object that's associated with the redirect.
        # This is so that if, for instance, Page(name="Front Page") is
        # only editable by a certain group, creating a Redirect from
        # "Front Page" to somewhere is similarly protected.
        if isinstance(obj, Redirect):
            return 'redirects.change_redirect'
        elif isinstance(obj, Page):
            return 'pages.change_page'


class RedirectDeleteView(PermissionRequiredMixin, RegionMixin, DeleteView):
    model = Redirect
    permission = 'redirects.delete_redirect'

    def get_object(self):
        source = slugify(self.kwargs.get('slug'))
        return Redirect.objects.get(source=source, region=self.get_region())

    def get_context_data(self, **kwargs):
        context = super(RedirectDeleteView, self).get_context_data(**kwargs)
        p = Page.objects.filter(slug=self.object.source, region=self.get_region())
        if p:
            context['page'] = p[0]
        else:
            context['page'] = Page(
                slug=self.object.source,
                name=self.object.source,
                region=self.object.region
            )
        return context

    def success_msg(self):
        # NOTE: This is eventually marked as safe when rendered in our
        # template.  So do *not* allow unescaped user input!
        return (
            '<div>' +\
            _('Thank you for your changes. ') +\
            _('The redirect has been deleted') +\
            '</div>' 
        )

    def get_success_url(self):
        return reverse('pages:show',
            args=[self.object.region, self.object.source])


class RedirectCompareView(RegionMixin, diff.views.CompareView):
    model = Redirect

    def get_object(self):
        return Redirect(
            source=slugify(self.kwargs.get('slug')), region=self.get_region())

    def get_context_data(self, **kwargs):
        context = super(RedirectCompareView, self).get_context_data(**kwargs)
        context['page'] = Page(
            slug=self.object.source,
            name=self.object.source,
            region=self.object.region
        )
        return context


class RedirectPermissionsView(SetPermissionsView):
    template_name = 'redirects/redirect_permissions.html'

    def get_object(self):
        return Redirect.objects.get(source=self.kwargs.get('slug'), region=self.get_region())

    def get_success_url(self):
        return '%s?show=1' % (reverse('pages:show', kwargs={
            'slug':self.get_object().source, 'region': self.get_region().slug
        }))

    def get_context_data(self, *args, **kwargs):
        context = super(RedirectPermissionsView, self).get_context_data(*args, **kwargs)
        redirect = self.get_object()
        context['page'] = Page(name=redirect.source, region=redirect.region)
        context['redirect'] = redirect
        return context
