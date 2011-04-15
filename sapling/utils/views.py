from django.utils.decorators import classonlymethod
from django.http import Http404, HttpResponseRedirect
from django.views.generic import DeleteView
from django.views.generic.edit import FormMixin

from forms import DeleteForm


class Custom404Mixin(object):
    @classonlymethod
    def as_view(cls, **initargs):
        default_view = super(Custom404Mixin, cls).as_view(**initargs)

        def view_or_handler404(request, *args, **kwargs):
            self = cls(**initargs)
            try:
                return default_view(request, *args, **kwargs)
            except Http404 as e:
                if hasattr(self, 'handler404'):
                    return self.handler404(request, *args, **kwargs)
                raise e
        return view_or_handler404


class CreateObjectMixin(object):
    def create_object(self):
        self.form_class._meta.model()

    def get_object(self, queryset=None):
        try:
            return super(CreateObjectMixin, self).get_object(queryset)
        except Http404:
            return self.create_object()


class DeleteView(DeleteView, FormMixin):
    form_class = DeleteForm

    def delete(self, *args, **kwargs):
        form = self.get_form(self.get_form_class())
        if form.is_valid():
            self.object = self.get_object()
            self.object.delete(comment=form.cleaned_data.get('comment'))
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(DeleteView, self).get_context_data(**kwargs)
        context['form'] = self.get_form(self.get_form_class())
        return context
