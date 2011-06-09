from django.contrib.gis.db import models
from django.contrib.gis.geos import *

from validators import validate_geometry


def flatten_collection(geoms):
    """
    Args:
        geoms: A GeometryCollection.

    Returns:
        A GeometryCollection where overlapping polygons are merged,
        and points/lines fully contained in polygons are removed.
    """
    # Iterate through all contained geometries, collecting all
    # polygons.
    polys = []
    other_geom = []
    for geom in geoms:
        if type(geom) == Polygon:
            polys.append(geom)
        else:
            other_geom.append(geom)

    # TODO: Maybe look into collapsing only overlapping polygons.
    # If we collapse only overlapping then we preserve the polygons'
    # "independence" in the editor -- when clicked on they will
    # appear as separate polygons.  I couldn't think of a way to do
    # this that wasn't a reimplementation of the cascading union
    # algorithm and it didn't seem worth it given that folks might
    # not care about this very minor detail.
    if polys:
        # Smash all polygons using a cascaded union.
        cascaded_poly = MultiPolygon(polys, srid=geoms.srid).cascaded_union
        # Skip points and lines that are fully contained in the flattened
        # polygon.
        flat_geoms = [cascaded_poly]
        for geom in other_geom:
            if not cascaded_poly.contains(geom):
                flat_geoms.append(geom)
    else:
        flat_geoms = other_geom

    return GeometryCollection(flat_geoms, srid=geoms.srid)


class CollectionFrom(models.GeometryCollectionField):
    """
    Creates a GeometryCollection pseudo-field from the provided
    component fields. When accessed, the CollectionFrom field will
    return a GeometryCollection from the provided component fields.
    When set to a value (upon model save) the geometries contained in
    the CollectionFrom field are broken out and placed into their
    relevant component fields.

    Example::

        class MyModel(models.Model):
            points = models.MultiPointField()
            lines = models.MultiLineStringField()
            polys = models.MultiPolygonField()
            geom = CollectionFrom(points='points', lines='lines',
                polys='polys')

    Then when you access the 'geom' attribute on instances of MyModel
    you'll get a GeometryCollection with your points, lines and polys.
    When you set the 'geom' attribute to a GeometryCollection and save
    an instance of MyModel the GeometryCollection is broken into points,
    lines and polygons and placed into the provided fields.

    This field is useful when you want to deal with GeometryCollections
    but still must maintain separate geometry fields on the model. For
    instance, GeoDjango does not currently allow you to filter (with
    geometry operations) based on GeometryCollections due to issues
    with the underlying libraries. Someday this may be fixed. But
    until then, we've got this Field.

    NOTES: This field will add a column to the db, but it won't ever
           store anything there except null. There's probably a way
           around this. TODO.
    """
    def __init__(self, *args, **kwargs):
        self.points_name = kwargs.pop('points') if 'points' in kwargs else None
        self.lines_name = kwargs.pop('lines') if 'lines' in kwargs else None
        self.polys_name = kwargs.pop('polys') if 'polys' in kwargs else None

        super(CollectionFrom, self).__init__(*args, **kwargs)
        self.null = True

    def contribute_to_class(self, cls, name):
        models.signals.class_prepared.connect(self.finalize, sender=cls)

        # Control the geometrycollection-like attribute via a special
        # descriptor.
        setattr(cls, name, CollectionDescriptor(self))

        # Back up the points, lines, polys attributes and then point them
        # to descriptors that, when set, clear out the
        # geometrycollection field.
        setattr(cls, '_explicit_%s' % self.points_name,
                getattr(cls, self.points_name))
        setattr(cls, self.points_name,
                ClearCollectionOnSet(self, self.points_name))
        setattr(cls, '_explicit_%s' % self.lines_name,
                getattr(cls, self.lines_name))
        setattr(cls, self.lines_name,
                ClearCollectionOnSet(self, self.lines_name))
        setattr(cls, '_explicit_%s' % self.polys_name,
                getattr(cls, self.polys_name))
        setattr(cls, self.polys_name,
                ClearCollectionOnSet(self, self.polys_name))

        super(models.GeometryField, self).contribute_to_class(cls, name)

    def finalize(self, sender, **kws):
        self._connected_to = sender
        models.signals.pre_save.connect(self.pre_model_save, sender=sender,
            weak=False)

    def pre_model_save(self, instance, raw, **kws):
        if not 'sender' in kws:
            return
        geom_collection = instance.__dict__.get(
            '_explicit_set_%s' % self.attname, None)
        if geom_collection is None:
            # They didn't set an explicit GeometryCollection.
            return
        points, lines, polys = [], [], []
        points_geom, lines_geom, polys_geom = None, None, None
        for geom in geom_collection:
            if type(geom) is Point:
                points.append(geom)
            if type(geom) is MultiPoint:
                points += [g for g in geom]
            if type(geom) is LineString or type(geom) is LinearRing:
                lines.append(geom)
            if type(geom) is MultiLineString:
                lines += [g for g in geom]
            if type(geom) is Polygon:
                polys.append(geom)
            if type(geom) is MultiPolygon:
                polys += [g for g in geom]

        if points:
            points_geom = MultiPoint(points, srid=points[0].srid)
        if lines:
            lines_geom = MultiLineString(lines, srid=lines[0].srid)
        if polys:
            polys_geom = MultiPolygon(polys, srid=polys[0].srid)

        setattr(instance, self.points_name, points_geom)
        setattr(instance, self.lines_name, lines_geom)
        setattr(instance, self.polys_name, polys_geom)

        # Set ourself to None to avoid saving any data in our column.
        setattr(instance, self.name, None)
        instance.__dict__[self.name] = None


class CollectionDescriptor(object):
    def __init__(self, field):
        self._field = field

    def __get__(self, instance=None, owner=None):
        if instance is None:
            raise AttributeError(
                "The '%s' attribute can only be accessed from %s instances."
                % (self._field.name, owner.__name__))

        set_field_value = instance.__dict__.get(
            '_explicit_set_%s' % self._field.attname, None)
        if set_field_value:
            # Return the value they set for the field rather than our
            # constructed GeometryCollection.
            return set_field_value

        enum_points, enum_lines, enum_polys = [], [], []
        points = getattr(instance, self._field.points_name)
        if points:
            enum_points = [p for p in points]
        lines = getattr(instance, self._field.lines_name)
        if lines:
            enum_lines = [l for l in lines]
        polys = getattr(instance, self._field.polys_name)
        if polys:
            enum_polys = [p for p in polys]

        geoms = enum_points + enum_lines + enum_polys

        collection = GeometryCollection(geoms, srid=self._field.srid)
        collection._from_get_on_owner = owner
        return collection

    def __set__(self, obj, value):
        # The OGC Geometry type of the field.
        gtype = self._field.geom_type

        # The geometry type must match that of the field -- unless the
        # general GeometryField is used.
        if (isinstance(value, GeometryCollection) and
            (str(value.geom_type).upper() == gtype or gtype == 'GEOMETRY')):
            # Assigning the SRID to the geometry.
            if value.srid is None:
                value.srid = self._field.srid
        elif value is None:
            pass
        elif isinstance(value, (basestring, buffer)):
            # Set with WKT, HEX, or WKB
            value = GEOSGeometry(value, srid=self._field.srid)
        else:
            raise TypeError(
                'cannot set %s CollectionFrom with value of type: %s' %
                (obj.__class__.__name__, type(value)))

        obj.__dict__['_explicit_set_%s' % self._field.attname] = value
        return value


class ClearCollectionOnSet(object):
    """
    A simple descriptor that, when set, clears out the stored
    geometry collection.  If we don't clear out the stored geometry
    collection when, say, the 'points' are set then we will end up
    with a stale geometry collection.
    """
    def __init__(self, field, attrname):
        self._field = field
        self._attrname = attrname

    def __get__(self, obj=None, owner=None):
        return getattr(obj, '_explicit_%s' % self._attrname)

    def __set__(self, obj, value):
        # If the GeometryCollection was explicitly set then let's clear it out,
        # as we've now set one of the component fields directly.
        if ('_explicit_set_%s' % self._field.attname) in obj.__dict__:
            del obj.__dict__['_explicit_set_%s' % self._field.attname]
        return setattr(obj, '_explicit_%s' % self._attrname, value)


class FlatCollectionFrom(CollectionFrom):
    """
    A CollectionFrom field that "flattens" overlapping polygons
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
        return super(FlatCollectionFrom, self).__init__(*args, **kws)

    def pre_model_save(self, instance, raw, **kws):
        geom = getattr(instance, self.attname)
        setattr(instance, self.attname, flatten_collection(geom))

        super(FlatCollectionFrom, self).pre_model_save(instance, raw, **kws)

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^maps\.fields"])
except ImportError:
    pass
