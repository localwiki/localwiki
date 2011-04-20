from django.utils.decorators import classonlymethod
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.views.generic import DeleteView, UpdateView, ListView
from django.views.generic.edit import FormMixin

from forms import DeleteForm, RevertForm


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


class HistoryView(ListView):
    context_object_name = 'version_list'
    template_name_suffix = '_history'
    revert_view_name = None

    def get_revert_view_name(self):
        if self.revert_view_name:
            return self.revert_view_name
        # We assume these are historical instances.
        if hasattr(self.object_list, 'model'):
            opts = self.object_list.model._original_model._meta
            return 'revert-%s' % opts.object_name.lower()

    def get_context_data(self, **kwargs):
        context = super(HistoryView, self).get_context_data(**kwargs)
        context['slug'] = self.kwargs.get('slug')
        context['revert_view'] = self.get_revert_view_name()
        return context

    def get_template_names(self):
        # We want obj_history not obj_hist_history.
        if hasattr(self.object_list, 'model'):
            hist_model = self.object_list.model
            self.object_list.model = hist_model._original_model
            names = super(HistoryView, self).get_template_names()
            self.object_list.model = hist_model
        return names


class UpdateView(UpdateView):
    """
    A subclass of the generic UpdateView that adds a message if the
    associated form was successfully merged.
    """
    success_msg = ("Thank you for your changes. "
                   "Your attention to detail is appreciated.")

    def form_valid(self, form):
        if getattr(form, 'performed_merge', None):
            messages.add_message(self.request, messages.WARNING,
                form.merge_success_msg)
        else:
            messages.add_message(self.request, messages.SUCCESS,
                self.success_msg)

        return super(UpdateView, self).form_valid(form)


class DeleteView(DeleteView, FormMixin):
    """
    A subclass of the generic DeleteView that passes along a comment
    with the delete().
    """
    form_class = DeleteForm
    success_msg = 'Successfully deleted!'

    def delete(self, *args, **kwargs):
        form = self.get_form(self.get_form_class())
        if form.is_valid():
            self.object = self.get_object()
            self.object.delete(comment=form.cleaned_data.get('comment'))
            messages.add_message(self.request, messages.SUCCESS,
                                 self.success_msg)
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(DeleteView, self).get_context_data(**kwargs)
        context['form'] = self.get_form(self.get_form_class())
        return context


# We subclass DeleteView here because the action flow is identical.
class RevertView(DeleteView):
    """
    View for reverting an object retrieved with `self.get_object()`,
    with a response rendered by template.  Has a confirmation form and
    passes a comment along to `revert_to()`.

    You'll need to define a `_confirm_revert` template, similar to
    `_confirm_delete`.
    """
    template_name_suffix = '_confirm_revert'
    form_class = RevertForm
    success_msg = 'Reverted to version %(version_number)s.'

    def __init__(self, *args, **kwargs):
        base_init = super(RevertView, self).__init__(*args, **kwargs)
        # We want object_confirm_revert, not object_hist_confirm_revert.
        if not self.template_name_field:
            self.template_name_field = self.context_object_name
        return base_init

    def get_object(self):
        obj = super(RevertView, self).get_object()
        return obj.history.as_of(version=int(self.kwargs['version']))

    def revert(self, *args, **kwargs):
        form = self.get_form(self.get_form_class())
        if form.is_valid():
            self.object = self.get_object()
            self.object.revert_to(comment=form.cleaned_data.get('comment'))
            version_number = self.object.history_info.version_number()
            messages.add_message(self.request, messages.SUCCESS,
                self.success_msg % {'version_number': version_number})
        return HttpResponseRedirect(self.get_success_url())

    def delete(self, *args, **kwargs):
        return self.revert(*args, **kwargs)

    def get_template_names(self):
        """
        We want obj_confirm_revert not obj_hist_confirm_revert.
        """
        orig_object = self.object
        # Temporarily swap out self.object with an instance of the
        # non-historical object for template-finding purposes.
        self.object = orig_object.history_info._object
        names = super(RevertView, self).get_template_names()
        self.object = orig_object
        return names
