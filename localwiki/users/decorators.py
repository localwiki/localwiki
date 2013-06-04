from guardian import decorators as guardian
from django.utils.functional import wraps
from django.http import Http404, HttpResponseForbidden


def permission_required(perm, lookup_variables=None, **kwargs):
    """
    Decorator for views that checks whether a user has a particular permission
    enabled.

    Based heavily on the django-guardian decorator and also uses it.

    Optionally, instances for which check should be made may be passed as an
    second argument or as a tuple of parameters same as those passed to
    ``get_object_or_404`` but must be provided as pairs of strings. If the
    the lookup fails because the object does not exist, falls back to checking
    permissions for the model.

    Examples::

        @permission_required('auth.change_user')
        def my_view(request):
            return HttpResponse('Hello')

        @permission_required('auth.change_user', (User, 'username', 'username'))
        def my_view(request, username):
            user = get_object_or_404(User, username=username)
            return user.get_absolute_url()

        @permission_required('auth.change_user',
            (User, 'username', 'username', 'groups__name', 'group_name'))
        def my_view(request, username, group_name):
            user = get_object_or_404(User, username=username,
                group__name=group_name)
            return user.get_absolute_url()

    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if lookup_variables:
                try:
                    return guardian.permission_required(perm, lookup_variables,
                        return_403=True)(view_func)(request, *args, **kwargs)
                except Http404:
                    pass
            if request.user.has_perm(perm):
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden('You do not have permissions to'
                                             ' perform this action.')
        return wraps(view_func)(_wrapped_view)
    return decorator
