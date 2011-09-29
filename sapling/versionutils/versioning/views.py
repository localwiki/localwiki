"""
A set of class-based views that make working with versioned models a
little more generic.  These views are modeled after django's
class-based generic views.
"""

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic import DeleteView, UpdateView, ListView
from django.views.generic.edit import FormMixin

from forms import DeleteForm, RevertForm


class VersionsList(ListView):
    """
    A subclass of django.views.generic.ListView.

    As with ListView, you need to provide get_queryset(). Your
    get_queryset() should return the historical queryset.
    Example::

        def get_queryset(self):
            all_page_history = Page(slug=self.kwargs['slug']).versions.all()
            # We set self.page to the most recent historical instance of the
            # page.
            self.page = all_page_history[0]
            return all_page_history
    """
    context_object_name = 'versions_list'
    template_name_suffix = '_versions'
    revert_view_name = None

    def get_context_data(self, **kwargs):
        context = super(VersionsList, self).get_context_data(**kwargs)
        context['slug'] = self.kwargs.get('slug')
        return context

    def get_template_names(self):
        # We want obj_history not obj_hist_history.
        if hasattr(self.object_list, 'model'):
            hist_model = self.object_list.model
            self.object_list.model = hist_model._original_model
            names = super(VersionsList, self).get_template_names()
            self.object_list.model = hist_model
        return names


class UpdateView(UpdateView):
    """
    A subclass of django.views.generic.UpdateView that that displays a
    form for editing an existing object, setting a message if the form
    was successfully merged, and redisplaying the form with validation
    errors (if there are any) and saving changes to the object. This
    uses a form automatically generated from the object's model class
    (unless a form class is manually specified).

    You can use this with or without versioning.forms.MergeMixin forms.
    """
    def success_msg(self):
        """
        Returns:
            A string that gets sent to django.contrib.messages'
            add_message() when the model is successfully saved.
        """
        return ("Thank you for your changes. "
                "Your attention to detail is appreciated.")

    def form_valid(self, form):
        if getattr(form, 'performed_merge', None):
            messages.add_message(self.request, messages.WARNING,
                form.merge_success_msg)
        else:
            messages.add_message(self.request, messages.SUCCESS,
                self.success_msg())

        return super(UpdateView, self).form_valid(form)


class DeleteView(DeleteView, FormMixin):
    """
    A subclass of django.views.generic.DeleteView. A view that displays
    a confirmation page with a comment form and deletes an existing
    object, passing along the comment to the historical instance. The
    given object will only be deleted if the request method is POST. If
    this view is fetched via GET, it will display a confirmation page.

    The delete confirmation page displayed to a GET request uses a
    template_name_suffix of '_confirm_delete'.
    """
    form_class = DeleteForm

    def success_msg(self):
        """
        Returns:
            A string that gets sent to django.contrib.messages'
            add_message() when the model is successfully deleted.
        """
        return 'Successfully deleted!'

    def delete(self, *args, **kwargs):
        form = self.get_form(self.get_form_class())
        if form.is_valid():
            self.object = self.get_object()
            self.object.delete(comment=form.cleaned_data.get('comment'))
            messages.add_message(self.request, messages.SUCCESS,
                                 self.success_msg())
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(DeleteView, self).get_context_data(**kwargs)
        context['form'] = self.get_form(self.get_form_class())
        return context


# We subclass DeleteView here because the action flow is identical.
class RevertView(DeleteView):
    """
    A view for reverting an object retrieved with self.get_object, with
    a response rendered by template. We display a confirmation page
    with a comment form and deletes an existing object, passing along
    the comment to the historical instance. The given object will only
    be deleted if the request method is POST. If this view is fetched
    via GET, it will display a confirmation page.

    The delete confirmation page displayed to a GET request uses a
    template_name_suffix of '_confirm_revert'.
    """
    template_name_suffix = '_confirm_revert'
    form_class = RevertForm

    def __init__(self, *args, **kwargs):
        base_init = super(RevertView, self).__init__(*args, **kwargs)
        # We want object_confirm_revert, not object_hist_confirm_revert.
        if not self.template_name_field:
            self.template_name_field = self.context_object_name
        return base_init

    def get_object(self):
        obj = super(RevertView, self).get_object()
        return obj.versions.as_of(version=int(self.kwargs['version']))

    def success_msg(self):
        version_number = self.object.version_info.version_number()
        return 'Reverted to version %s.' % version_number

    def revert(self, *args, **kwargs):
        form = self.get_form(self.get_form_class())
        if form.is_valid():
            self.object = self.get_object()
            self.object.revert_to(comment=form.cleaned_data.get('comment'))
            messages.add_message(self.request, messages.SUCCESS,
                self.success_msg())
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
        self.object = orig_object.version_info._object
        names = super(RevertView, self).get_template_names()
        self.object = orig_object
        return names
