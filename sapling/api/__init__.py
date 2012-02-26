from django.conf.urls.defaults import url

from tastypie.api import Api
from tastypie.bundle import Bundle

from pages.models import slugify, name_to_url


class SlugifyMixin(object):
    def obj_get(self, request=None, **kwargs):
        kwargs['slug'] = slugify(kwargs['slug'])
        return super(SlugifyMixin, self).obj_get(request=request, **kwargs)

    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<slug>.+?)/*$" %
                self._meta.resource_name, self.wrap_view('dispatch_detail'),
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

        slugify_from_field = getattr(self._meta, 'slugify_from_field', 'slug')
        kwargs['slug'] = name_to_url(getattr(obj, slugify_from_field))

        if self._meta.api_name is not None:
            kwargs['api_name'] = self._meta.api_name

        return self._build_reverse_url("api_dispatch_detail", kwargs=kwargs)

api = Api(api_name='v1')
