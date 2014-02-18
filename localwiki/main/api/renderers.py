from rest_framework.renderers import BrowsableAPIRenderer


class LocalWikiAPIRenderer(BrowsableAPIRenderer):
    def get_breadcrumbs(self, request):
        crumbs_verbose = super(LocalWikiAPIRenderer, self).get_breadcrumbs(request)

        crumbs = []
        for name, url in crumbs_verbose:
            name = url.rstrip('/')
            name = name.split('/')[-1]
            crumbs.append((name, url))
        return crumbs
