from django.conf import settings
from django import forms
from django.contrib.gis.geos import GeometryCollection, GEOSGeometry

from olwidget.forms import MapModelForm

from versionutils.merging.forms import MergeMixin
from versionutils.versioning.forms import CommentMixin
from models import MapData
from widgets import MediaMixin

OLWIDGET_OPTIONS = None
if hasattr(settings, 'OLWIDGET_DEFAULT_OPTIONS'):
    OLWIDGET_OPTIONS = settings.OLWIDGET_DEFAULT_OPTIONS


class MapForm(MergeMixin, CommentMixin, MediaMixin, MapModelForm):
    class Meta:
        model = MapData
        exclude = ('page', 'points', 'lines', 'polys')
        options = OLWIDGET_OPTIONS

    def merge(self, yours, theirs, ancestor):
        (merged_content, conflict) = self._map_merge(
            yours.get('geom'),
            theirs.get('geom')[0],  # olwidget has form.initial set to a list
            ancestor.get('geom')
        )
        if conflict:
            self.data = self.data.copy()
            self.data['geom'] = merged_content
            raise forms.ValidationError(self.conflict_error)
        else:
            yours['geom'] = merged_content
        return yours

    def _map_merge(self, yours, theirs, ancestor):
        """
        Merge yours and theirs.  Return a conflict message if there was
        a merge conflict.
        """
        yours_added, yours_deleted = self._get_add_del(yours, ancestor)
        theirs_added, theirs_deleted = self._get_add_del(theirs, ancestor)

        # Look at the union of what was added + deleted in theirs and
        # ours.  If there's an overlap in these changes then we want to
        # display a conflict message.
        yours_changed = yours_added.union(yours_deleted)
        theirs_changed = theirs_added.union(theirs_deleted)
        has_conflict = yours_changed.intersects(theirs_changed)

        # The merged material should be:
        # our geometries + theirs that were added - theirs that were
        # deleted *if* it wasn't already deleted in ours.

        # We use str(geom) here because we want easy containment testing
        # of geometries in sets.
        yours_deleted_set = set([str(g) for g in yours_deleted])
        merged = set([str(g) for g in yours] + [str(g) for g in theirs_added])
        for geom in theirs_deleted:
            if str(geom) not in yours_deleted_set:
                merged.remove(str(geom))

        merged_geom = GeometryCollection(
            [GEOSGeometry(s) for s in merged], srid=yours.srid)
        return (merged_geom, has_conflict)

    def _get_add_del(self, geoms, ancestor):
        """
        Find the geometries that were added and deleted in geoms
        when compared to the ancestor.
        """
        added, deleted = [], []
        ancestor_set = set([str(g) for g in ancestor])
        geoms_set = set([str(g) for g in geoms])

        for geom in geoms:
            if not str(geom) in ancestor_set:
                added.append(geom)
        for geom in ancestor:
            if not str(geom) in geoms_set:
                deleted.append(geom)
        added = GeometryCollection([GEOSGeometry(s) for s in added],
            srid=geoms.srid)
        deleted = GeometryCollection([GEOSGeometry(s) for s in deleted],
            srid=geoms.srid)
        return (added, deleted)
