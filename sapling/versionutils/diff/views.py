from dateutil.parser import parse as dateparser

from django.shortcuts import render_to_response
from django.views.generic import DetailView
from django.http import Http404

from versionutils.versioning import get_versions


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

        if self.kwargs.get('date1'):
            # Using datetimes to display diff.
            date1 = self.kwargs.get('date1')
            date2 = self.kwargs.get('date2')
            # Query parameter list used in history compare view.
            dates = self.request.GET.getlist('date')
            if not dates:
                dates = [v for v in (date1, date2) if v]
            dates = [dateparser(v) for v in dates]
            old = min(dates)
            new = max(dates)
            new_version = get_versions(self.object).as_of(date=new)
            prev_version = new_version.version_info.version_number() - 1
            if len(dates) == 1 and prev_version > 0:
                old_version = get_versions(self.object).as_of(
                    version=prev_version)
            elif prev_version <= 0:
                old_version = None
            else:
                old_version = get_versions(self.object).as_of(date=old)
        else:
            # Using version numbers to display diff.
            version1 = self.kwargs.get('version1')
            version2 = self.kwargs.get('version2')
            # Query parameter list used in history compare view.
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
            if old > 0:
                old_version = get_versions(self.object).as_of(version=old)
            else:
                old_version = None
            new_version = get_versions(self.object).as_of(version=new)

        context.update({'old': old_version, 'new': new_version})
        return context


def debug(request):
    info = {
      'message': 'hi',
    }
    return render_to_response('debug.html', {'info': info})
