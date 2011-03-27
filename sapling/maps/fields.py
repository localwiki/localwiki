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
    def __init__(self, *args, **kwargs):
        # Ensure the geometry provided is valid.
        validators = kwargs.get('validators', [])
        if not validate_geometry in validators:
            validators.append(validate_geometry)
        kwargs['validators'] = validators
        return super(FlatGeometryCollectionField, self).__init__(*args, **kwargs)

    def _flatten(self, geom_collection):
        # Iterate through all contained geometries, collecting all
        # polygons.
        mp_list = []
        other_geom = []
        for geom in geom_collection:
            if type(geom) == Polygon:
                mp_list.append(geom)
            else:
                other_geom.append(geom)
        
        # Take collected polygons and flatten them together in a
        # cascaded union.
        return GeometryCollection(
            MultiPolygon(mp_list, srid=geom_collection.srid).cascaded_union,
            srid=geom_collection.srid
        )

    def pre_save(self, instance, add):
        geom = getattr(instance, self.attname)
        flat_geom = self._flatten(geom)

        setattr(instance, self.attname, flat_geom)
        return flat_geom
