from lxml.html import document_fromstring

from django.conf import settings
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings
from django.contrib.auth.models import User

from . import take_n_from


class TakeNFromTests(TestCase):
    def setUp(self):
        self.pages = ['front page', 'duboce park', 'cows on fire', 'farts', 'more cows', 'duboce park', 'hi']
        self.pages = sorted(self.pages, reverse=True)
        self.maps = ['front page map', 'corn', 'holy', 'apple']
        self.maps = sorted(self.maps, reverse=True)
        self.files = ['front page', 'duboce park whoa', 'aaaaaaaaaaaaaaa', 'aaaa', 'aaa']
        self.files = sorted(self.files, reverse=True)

    def test_basic_take(self):
        ls = ((self.pages, 0), (self.maps, 0), (self.files, 0))

        all_sorted = sorted(self.pages + self.maps + self.files, reverse=True)

        items, indexes, more_left = take_n_from(ls, 3, merge_key=(lambda x: x))
        self.assertEqual(items, all_sorted[:3])
        self.assertEqual(indexes, [2, 1, 0])

    def test_take_general(self):
        ls = ((self.pages, 0), (self.maps, 0), (self.files, 0))

        all_sorted = sorted(self.pages + self.maps + self.files, reverse=True)

        for i in range(0, len(all_sorted)):
            items, indexes, more_left = take_n_from(ls, i, merge_key=(lambda x: x))
            self.assertEqual(items, all_sorted[:i])

    def test_take_more_than_left(self):
        ls = ((self.pages, 0), (self.maps, 0), (self.files, 0))

        all_sorted = sorted(self.pages + self.maps + self.files, reverse=True)

        items, indexes, more_left = take_n_from(ls, len(all_sorted) + 1, merge_key=(lambda x: x))
        self.assertEqual(len(items), len(all_sorted))


class CanonicalURLTests(TestCase):
    def has_canonical_url(self, html, url):
        doc = document_fromstring(html)
        canonical_urls = doc.findall('.//link[@rel="canonical"]')

        if len(canonical_urls) != 1:
            return False

        return (canonical_urls[0].attrib['href'] == url)

    def setUp(self):
        from regions.models import Region
        from pages.models import Page

        self.factory = RequestFactory()

        # Create a new region and associate a domain with it
        self.sf = Region(full_name="San Francisco", slug="sf")
        self.sf.save()
        self.sf.regionsettings.domain = 'fakename.org'
        self.sf.regionsettings.save()
       
        # Create a page in the SF region
        p = Page(name='Parks', content='<p>Hi</p>', region=self.sf)
        p.save()

        self.user = User.objects.create_user(
            username='testuser', email='testuser@example.org', password='fakepassword')

    @override_settings(CUSTOM_HOSTNAMES=['fakename.org'])
    def test_canonical_front_page(self):
        from frontpage.views import FrontPageView
        from django_hosts.middleware import HostsMiddlewareRequest

        #####################################################
        # Just the default / page in a custom domain region
        #####################################################

        request = self.factory.get('/')
        request.user = self.user
        request.META['HTTP_HOST'] = self.sf.regionsettings.domain

        middleware = HostsMiddlewareRequest()
        middleware.process_request(request)

        view = FrontPageView.as_view()
        response = view(request)

        canonical_url = '//%s/sf/' % settings.MAIN_HOSTNAME
        response.render()
        self.assertTrue(self.has_canonical_url(response.content, canonical_url))

        #####################################################
        # The /Front_Page page in a custom domain region.
        #####################################################

        request = self.factory.get('/Front_Page')
        request.user = self.user
        request.META['HTTP_HOST'] = self.sf.regionsettings.domain

        middleware = HostsMiddlewareRequest()
        middleware.process_request(request)

        view = FrontPageView.as_view()
        response = view(request)

        canonical_url = '//%s/sf/' % settings.MAIN_HOSTNAME
        response.render()
        self.assertTrue(self.has_canonical_url(response.content, canonical_url))

        #####################################################
        # The /Front_Page page on the main host inside region
        ##################################################### 
        
        request = self.factory.get('/sf/Front_Page')
        request.user = self.user
        request.META['HTTP_HOST'] = settings.MAIN_HOSTNAME

        middleware = HostsMiddlewareRequest()
        middleware.process_request(request)

        view = FrontPageView.as_view()
        response = view(request, region='sf')

        canonical_url = '/sf/'
        response.render()
        self.assertTrue(self.has_canonical_url(response.content, canonical_url))

        #####################################################
        # The /FRONT_pAgE (changed capitalization)
        ##################################################### 
        
        request = self.factory.get('/sf/FRONT_pAgE')
        request.user = self.user
        request.META['HTTP_HOST'] = settings.MAIN_HOSTNAME

        middleware = HostsMiddlewareRequest()
        middleware.process_request(request)

        view = FrontPageView.as_view()
        response = view(request, region='sf')

        canonical_url = '/sf/'
        response.render()
        self.assertTrue(self.has_canonical_url(response.content, canonical_url))


    @override_settings(CUSTOM_HOSTNAMES=['fakename.org'])
    def test_canonical_page_names(self):
        from pages.views import PageDetailView
        from pages.urls import slugify
        from django_hosts.middleware import HostsMiddlewareRequest

        #####################################################
        # A regular page on a custom domain
        #####################################################

        request = self.factory.get('/Parks')
        request.user = self.user
        request.META['HTTP_HOST'] = self.sf.regionsettings.domain

        middleware = HostsMiddlewareRequest()
        middleware.process_request(request)

        view = slugify(PageDetailView.as_view())
        response = view(request, slug='Parks')

        canonical_url = '//%s/sf/Parks' % settings.MAIN_HOSTNAME
        response.render()
        self.assertTrue(self.has_canonical_url(response.content, canonical_url))

        #####################################################
        # Now let's try it with an alternative capitalization
        #####################################################

        request = self.factory.get('/PArkS')
        request.user = self.user
        request.META['HTTP_HOST'] = self.sf.regionsettings.domain

        middleware = HostsMiddlewareRequest()
        middleware.process_request(request)

        view = slugify(PageDetailView.as_view())
        response = view(request, slug='PArkS')

        canonical_url = '//%s/sf/Parks' % settings.MAIN_HOSTNAME
        response.render()
        self.assertTrue(self.has_canonical_url(response.content, canonical_url))

        #####################################################
        # Regular page viewing directly on the main host
        #####################################################

        request = self.factory.get('/sf/Parks')
        request.user = self.user
        request.META['HTTP_HOST'] = self.sf.regionsettings.domain

        middleware = HostsMiddlewareRequest()
        middleware.process_request(request)

        view = slugify(PageDetailView.as_view())
        response = view(request, slug='Parks', region='sf')

        response.render()
        # Directly on the canonical url, so it shouldn't be rendered
        self.assertFalse(self.has_canonical_url(response.content, ''))

        #####################################################
        # Capitalization variant viewed on the main host
        #####################################################

        request = self.factory.get('/sf/PArks')
        request.user = self.user
        request.META['HTTP_HOST'] = self.sf.regionsettings.domain

        middleware = HostsMiddlewareRequest()
        middleware.process_request(request)

        view = slugify(PageDetailView.as_view())
        response = view(request, slug='PArks', region='sf')

        canonical_url = '/sf/Parks'
        response.render()
        self.assertFalse(self.has_canonical_url(response.content, canonical_url))

    @override_settings(CUSTOM_HOSTNAMES=['fakename.org'])
    def test_canonical_search(self):
        from search.urls import haystack_search, global_search
        from django_hosts.middleware import HostsMiddlewareRequest

        #####################################################
        # Search page on custom domain
        #####################################################

        request = self.factory.get('/_rsearch/?q=parks')
        request.user = self.user
        request.META['HTTP_HOST'] = self.sf.regionsettings.domain

        middleware = HostsMiddlewareRequest()
        middleware.process_request(request)

        view = haystack_search
        response = view(request)

        canonical_url = '//%s/_rsearch/sf?q=parks' % settings.MAIN_HOSTNAME
        self.assertTrue(self.has_canonical_url(response.content, canonical_url))

        #####################################################
        # Search page on main domain
        #####################################################

        request = self.factory.get('/_rsearch/sf?q=parks')
        request.user = self.user
        request.META['HTTP_HOST'] = settings.MAIN_HOSTNAME

        middleware = HostsMiddlewareRequest()
        middleware.process_request(request)

        view = haystack_search
        response = view(request, region='sf')

        canonical_url = ''
        # On host, so no canonical url
        self.assertFalse(self.has_canonical_url(response.content, canonical_url))
