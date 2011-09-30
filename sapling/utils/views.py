from django.utils.decorators import classonlymethod, method_decorator
from guardian.decorators import permission_required
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.utils import simplejson as json


class ForbiddenException:
    pass


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


class JSONResponseMixin(object):
    def render_to_response(self, context):
        "Returns a JSON response containing 'context' as payload"
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        "Construct an `HttpResponse` object."
        return HttpResponse(content, content_type='application/json',
                            **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        '''Convert the context dictionary into a JSON object.
        Note: Make sure that the entire context dictionary is serializable
        '''
        return json.dumps(context)


class PermissionRequiredMixin(object):
    """
    View mixin for verifying permissions before updating an existing object
    """
    permission = None
    forbidden_message = 'Sorry, you are not allowed to perform this action.'

    def get_protected_object(self):
        """ Returns the object that should be used to check permissions.
        Override this to use a different object as the "guard".
        """
        return self.object

    def get_object_idempotent(self):
        return self.object

    def patch_get_object(self):
        # Since get_object will get called again, we want it to be idempotent
        self.get_object = self.get_object_idempotent

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        protected_object = None
        if hasattr(self, 'get_object'):
            self.object = self.get_object()
            self.patch_get_object()
            protected_object = self.get_protected_object()
        if not request.user.has_perm(self.permission, protected_object):
            return HttpResponseForbidden(self.forbidden_message)
        return super(PermissionRequiredMixin, self).dispatch(request, *args,
                                                        **kwargs)
