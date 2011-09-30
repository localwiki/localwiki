from django.core.urlresolvers import reverse

from versionutils.versioning.views import UpdateView, DeleteView
from versionutils import diff
from utils.views import CreateObjectMixin, PermissionRequiredMixin
from pages.models import Page, slugify

from models import Redirect
from forms import RedirectForm


class RedirectUpdateView(PermissionRequiredMixin, CreateObjectMixin,
        UpdateView):
    model = Redirect
    form_class = RedirectForm

    def get_object(self):
        source = slugify(self.kwargs.get('slug'))
        redirect = Redirect.objects.filter(source=source)
        if redirect:
            return redirect[0]
        return Redirect(source=source)

    def get_context_data(self, **kwargs):
        context = super(RedirectUpdateView, self).get_context_data(**kwargs)
        p = Page.objects.filter(slug=self.object.source)
        if p:
            context['page'] = p[0]
        else:
            context['page'] = Page(slug=self.object.source,
                name=self.object.source)
        context['exists'] = Redirect.objects.filter(source=self.object.source)
        return context

    def success_msg(self):
        # NOTE: This is eventually marked as safe when rendered in our
        # template.  So do *not* allow unescaped user input!
        return (
            '<div>Thank you for your changes. '
            'This page now redirects to <a href="%s">%s</a>.</div>'
            % (self.object.destination.get_absolute_url(),
               self.object)
        )

    def get_success_url(self):
        return reverse('pages:show', args=[self.object.source])

    def create_object(self):
        return Redirect(source=slugify(self.kwargs['slug']))

    def get_protected_objects(self):
        protected = []
        slug = slugify(self.kwargs['slug'])

        page = Page.objects.filter(slug=slug)
        if page:
            protected.append(page[0])
        redirect = Redirect.objects.filter(source=slug)
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


class RedirectDeleteView(DeleteView):
    model = Redirect

    def get_object(self):
        source = slugify(self.kwargs.get('slug'))
        return Redirect.objects.get(source=source)

    def get_context_data(self, **kwargs):
        context = super(RedirectDeleteView, self).get_context_data(**kwargs)
        p = Page.objects.filter(slug=self.object.source)
        if p:
            context['page'] = p[0]
        else:
            context['page'] = Page(slug=self.object.source,
                name=self.object.source)
        return context

    def success_msg(self):
        # NOTE: This is eventually marked as safe when rendered in our
        # template.  So do *not* allow unescaped user input!
        return (
            '<div>Thank you for your changes. '
            'The redirect has been deleted</div>'
        )

    def get_success_url(self):
        return reverse('pages:show', args=[self.object.source])


class RedirectCompareView(diff.views.CompareView):
    model = Redirect

    def get_object(self):
        return Redirect(source=slugify(self.kwargs.get('slug')))

    def get_context_data(self, **kwargs):
        context = super(RedirectCompareView, self).get_context_data(**kwargs)
        context['page'] = Page(slug=self.object.source,
            name=self.object.source)
        return context
