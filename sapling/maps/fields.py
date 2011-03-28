from django.contrib.gis.db import models
from django.contrib.gis.geos import Polygon, MultiPolygon, GeometryCollection

from validators import validate_geometry


class FlatGeometryCollectionField(models.GeometryCollectionField):
    """
    A GeometryCollectionField that "flattens" overlapping polygons
    together.  Additionally, we validate that the geometry provided to
    the field is valid.

    Raises:
        ValidationError: If the provided geometry is not valid.
    """
    def __init__(self, *args, **kws):
        # Ensure the geometry provided is valid.
        validators = kws.get('validators', [])
        if not validate_geometry in validators:
            validators.append(validate_geometry)
        kws['validators'] = validators
        return super(FlatGeometryCollectionField, self).__init__(*args, **kws)

    def _flatten(self, geoms):
        # Iterate through all contained geometries, collecting all
        # polygons.
        polys = []
        other_geom = []
        for geom in geoms:
            if type(geom) == Polygon:
                polys.append(geom)
            else:
                other_geom.append(geom)

        # TODO: Look into collapsing only overlapping polygons.  If we
        # collapse only overlapping then we preserve the polygons'
        # "independence" in the editor -- when clicked on they will
        # appear as separate polygons.  I couldn't think of a way to do
        # this that wasn't a reimplementation of the cascading union
        # algorithm and it didn't seem worth it given that folks might
        # not care about this very minor detail.
        if polys:
            # Smash all polygons using a cascaded union.
            cascaded_poly = MultiPolygon(polys, srid=geoms.srid).cascaded_union
            # Skip points and lines that are fully contained in the flattened
            # polygons.
            flat_geoms = [cascaded_poly]
            for geom in other_geom:
                if not cascaded_poly.contains(geom):
                    flat_geoms.append(geom)
        else:
            flat_geoms = other_geom

        return GeometryCollection(flat_geoms, srid=geoms.srid)

    def pre_save(self, instance, add):
        geom = getattr(instance, self.attname)
        flat_geom = self._flatten(geom)

        setattr(instance, self.attname, flat_geom)
        return flat_geom
