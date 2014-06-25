import re
from copy import copy

from django.template import Library, Node
from django.template.defaulttags import URLNode
from django.utils.encoding import smart_text
from django.conf import settings
from django.template import TemplateSyntaxError

from django_hosts.templatetags.hosts import HostURLNode

from regions.models import Region, RegionSettings

register = Library()

kwarg_re = re.compile(r"(?:(\w+)=)?(.+)")


@register.tag
def url(parser, token):
    """
    A smarter version of the default Django {% url %} tag that will render
    host-aware URLs.  E.g. if the requested URL is within this LocalWiki
    region, it will be relative.  If the rquested URL is /from/ a 
    LocalWiki region with a custom domain /to/ the rest of LocalWiki, it
    will be rendered as absolute.

    TODO: This should become irrelevant at some point, as the custom
          domain names only apply for a very, very select number of
          LocalWiki regions with no plans to expand at the moment.
    """
    return SmartURLNode.handle_token(parser, token)


class CustomURLConfURLNode(URLNode):
    # Copy/pasted from defaulttags.URLNode because there's no
    # easy other way to do this because of the hard-coding
    # on reverse().
    def __init__(self, view_name, args, kwargs, asvar, urlconf=None, remove_region_slug=False):
        self.view_name = view_name
        self.args = args
        self.kwargs = kwargs
        self.original_kwargs = copy(kwargs)
        self.asvar = asvar
        self.urlconf = urlconf
        self.remove_region_slug = remove_region_slug

        # Remove 'region' kwarg, if present, as we don't use the 'region' slug
        # in our custom-domain based urlpatterns.
        if self.remove_region_slug:
            if 'region' in self.kwargs:
                del self.kwargs['region']

    def render(self, context):
        from django.core.urlresolvers import reverse, NoReverseMatch
        args = [arg.resolve(context) for arg in self.args]
        kwargs = dict([(smart_text(k, 'ascii'), v.resolve(context))
                       for k, v in self.kwargs.items()])

        view_name = self.view_name.resolve(context)

        if not view_name:
            raise NoReverseMatch("'url' requires a non-empty first argument. "
                "The syntax changed in Django 1.5, see the docs.")

        # Try to look up the URL twice: once given the view name, and again
        # relative to what we guess is the "main" app. If they both fail,
        # re-raise the NoReverseMatch unless we're using the
        # {% url ... as var %} construct in which case return nothing.
        url = ''
        try:
            url = reverse(view_name, args=args, kwargs=kwargs, current_app=context.current_app, urlconf=self.urlconf)
        except NoReverseMatch as e:
            if settings.SETTINGS_MODULE:
                project_name = settings.SETTINGS_MODULE.split('.')[0]
                try:
                    url = reverse(project_name + '.' + view_name,
                              args=args, kwargs=kwargs,
                              current_app=context.current_app)
                except NoReverseMatch:
                    if self.urlconf != settings.ROOT_URLCONF:
                        # Re-try to match on the base urlconf instead, and render as an absolute URL.
                        try:
                            host = settings.DEFAULT_HOST
                            host_args, host_kwargs = (), {}
                            return HostURLNode(host, self.view_name, host_args, host_kwargs, self.args, self.original_kwargs, self.asvar).render(context)
                        except:
                            pass

                    if self.asvar is None:
                        # Re-raise the original exception, not the one with
                        # the path relative to the project. This makes a
                        # better error message.
                        raise e
            else:
                if self.asvar is None:
                    raise e

        if self.asvar:
            context[self.asvar] = url
            return ''
        else:
            return url


class SmartURLNode(Node):
    @classmethod
    def parse_params(cls, parser, bits):
        args, kwargs = [], {}
        for bit in bits:
            name, value = kwarg_re.match(bit).groups()
            if name:
                kwargs[name] = parser.compile_filter(value)
            else:
                args.append(parser.compile_filter(value))
        return args, kwargs

    @classmethod
    def handle_token(cls, parser, token):
        bits = token.split_contents()
        name = bits[0]
        if len(bits) < 2:
            raise TemplateSyntaxError("'%s' takes at least 1 argument" % name)

        try:
            view_name = parser.compile_filter(bits[1])
        except TemplateSyntaxError as exc:
            exc.args = (exc.args[0] + ". "
                    "The syntax of 'url' changed in Django 1.5, see the docs."),
            raise

        bits = bits[1:]  # Strip off view
        asvar = None
        if 'as' in bits:
            pivot = bits.index('as')
            try:
                asvar = bits[pivot + 1]
            except IndexError:
                raise TemplateSyntaxError("'%s' arguments must include "
                                          "a variable name after 'as'" % name)
            del bits[pivot:pivot + 2]

        view_args, view_kwargs = cls.parse_params(parser, bits[1:])
        return cls(parser, token, view_name, view_args, view_kwargs, asvar)

    def __init__(self, parser, token, view_name, view_args, view_kwargs, asvar):
        self.parser = parser
        self.token = token
        self.view_name = view_name
        self.view_args = view_args
        self.view_kwargs = view_kwargs
        self.asvar = asvar
        self.region_linking_to_slug = view_kwargs.get('region')

    def render_url_tag(self, context, urlconf=None, remove_region_slug=False):
        return CustomURLConfURLNode(
            self.view_name,
            self.view_args,
            self.view_kwargs,
            self.asvar,
            urlconf=urlconf,
            remove_region_slug=remove_region_slug
        ).render(context)

    def render_host_url_tag(self, context):
        host = settings.DEFAULT_HOST
        host_args, host_kwargs = (), {}
        return HostURLNode(host, self.view_name, host_args, host_kwargs, self.view_args, self.view_kwargs, self.asvar).render(context)

    def render(self, context):
        if not 'request' in context:
            return self.render_url_tag(context)

        request = context['request']

        cur_hostname = request.META['HTTP_HOST']
        cur_region_with_domain = None
        region_linking_to = None
        urlconf = None

        if self.region_linking_to_slug:
            region_linking_to_slug = self.region_linking_to_slug.resolve('context')
        else:
            region_linking_to_slug = None

        # Get the current region, if we're rendering on a region wth a
        # custom domain.
        in_region_with_custom_domain = RegionSettings.objects.filter(domain=cur_hostname)
        if in_region_with_custom_domain:
            cur_region_with_domain  = in_region_with_custom_domain[0]
            cur_region_with_domain = cur_region_with_domain.region

        # Get the region object we're linking to, if possible.
        if region_linking_to_slug:
            region_linking_to = Region.objects.filter(slug=region_linking_to_slug)
            if region_linking_to:
                region_linking_to = region_linking_to[0]

        if in_region_with_custom_domain:
            explicit_link_to_self = region_linking_to and (cur_region_with_domain == region_linking_to)
            if getattr(request, 'host'):
                urlconf = request.host.urlconf

            # We're linking inside of the region, so let's
            # just use the usual URL tag, but with the host
            # specific URLconf.
            if explicit_link_to_self or not region_linking_to:
                return self.render_url_tag(context, urlconf=urlconf, remove_region_slug=True)

            # A link outside the region, so let's render it as absolute.
            return self.render_host_url_tag(context)
        else:
            # Otherwise, we always use the usual URL tag and
            # don't route to the custom domain name.
            return self.render_url_tag(context)
