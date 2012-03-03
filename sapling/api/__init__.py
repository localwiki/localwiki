from django.conf.urls.defaults import *

from tastypie.api import Api, AcceptHeaderRouter
from tastypie.bundle import Bundle

from pages.models import slugify, name_to_url


class SlugifyMixin(object):
    """
    Add this mixin to your Resource model to lookup resource entries by a
    slugified value rather than by integer primary key. This mixin will make
    your resources resource_uri more human readable.

    There are two Meta attributes::

        field_to_slugify: A string representing the name of the field that
            will by slugified. slugify() is called on this field. If not
            provided, the value of slug_lookup_field is used.

        slug_lookup_field: A string representing the name of the field that
            we use for the slug lookup on the model.  If not provided, the
            value 'slug' is used.
    """
    def obj_get(self, request=None, **kwargs):
        slug = getattr(self._meta, 'slug_lookup_field', 'slug')
        kwargs[slug] = slugify(kwargs[slug])
        return super(SlugifyMixin, self).obj_get(request=request, **kwargs)

    def override_urls(self):
        slug = getattr(self._meta, 'slug_lookup_field', 'slug')
        return [
            url(r"^(?P<resource_name>%s)/(?P<%s>.+?)/*$" %
                (self._meta.resource_name, slug),
                self.wrap_view('dispatch_detail'),
                name="api_dispatch_detail"),
        ]

    def get_resource_uri(self, bundle_or_obj):
        kwargs = {
            'resource_name': self._meta.resource_name,
        }

        if isinstance(bundle_or_obj, Bundle):
            obj = bundle_or_obj.obj
        else:
            obj = bundle_or_obj

        slug = getattr(self._meta, 'slug_lookup_field', 'slug')
        field_to_slugify = getattr(self._meta, 'field_to_slugify', slug)

        kwargs[slug] = name_to_url(getattr(obj, field_to_slugify))

        if (self._meta.api_name is not None and
            not self._meta._api._accept_header_routing):
            kwargs['api_name'] = self._meta.api_name

        return self._build_reverse_url("api_dispatch_detail", kwargs=kwargs)

api_router = AcceptHeaderRouter()
api = Api(api_name='v1')
api_router.register(api, default=True)
