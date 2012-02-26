from django.conf.urls.defaults import url

from tastypie.api import Api
from tastypie.bundle import Bundle

from pages.models import slugify, name_to_url


class SlugifyMixin(object):
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
        field_to_slug = getattr(self._meta, 'field_to_slug', slug)

        kwargs[slug] = name_to_url(getattr(obj, field_to_slug))

        if self._meta.api_name is not None:
            kwargs['api_name'] = self._meta.api_name

        return self._build_reverse_url("api_dispatch_detail", kwargs=kwargs)


api = Api(api_name='v1')
