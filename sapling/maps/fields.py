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
        polygons = []
        other_geom = []
        for geom in geom_collection:
            if type(geom) == Polygon:
                polygons.append(geom)
            else:
                other_geom.append(geom)
        all_geom = other_geom

        # Take all polygons and smash them together using
        # cascaded_union.
        if polygons:
            all_geom.append(MultiPolygon(polygons, srid=geom_collection.srid).cascaded_union)
        
        return GeometryCollection(all_geom, srid=geom_collection.srid)

    def pre_save(self, instance, add):
        geom = getattr(instance, self.attname)
        flat_geom = self._flatten(geom)

        setattr(instance, self.attname, flat_geom)
        return flat_geom
