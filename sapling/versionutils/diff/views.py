from django.shortcuts import render_to_response
from django.views.generic import DetailView
from django.http import Http404


class CompareView(DetailView):
    """
    A Class-based view used for displaying a difference.  Attributes and
    methods are similar to the standard DetailView.

    Attributes:
        model: The model the diff acts on.
    """
    template_name_suffix = '_diff'

    def get_context_data(self, **kwargs):
        context = super(CompareView, self).get_context_data(**kwargs)

        version1 = self.kwargs.get('verison1')
        version2 = self.kwargs.get('version2')
        versions = self.request.GET.getlist('version')
        if not versions:
            versions = [v for v in (version1, version2) if v]
        if not versions:
            raise Http404("Versions not specified")
        versions = [int(v) for v in versions]
        old = min(versions)
        new = max(versions)
        if len(versions) == 1:
            old = max(new - 1, 1)
        old_version = self.object.history.as_of(version=old)
        new_version = self.object.history.as_of(version=new)

        context.update({'old': old_version, 'new': new_version})
        return context


def debug(request):
    info = {
      'message': 'hi',
    }
    return render_to_response('debug.html', {'info': info})
