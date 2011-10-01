from django.core.urlresolvers import reverse

from versionutils.versioning.views import UpdateView
from utils.views import CreateObjectMixin
from pages.models import Page, slugify

from models import Redirect
from forms import RedirectForm


class RedirectUpdateView(CreateObjectMixin, UpdateView):
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
            context['page'] = Page(slug=self.object.source, name=self.object.source)
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
