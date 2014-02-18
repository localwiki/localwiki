from django.test import TestCase
from django.core.files.base import ContentFile
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.auth.models import User

from regions.models import Region, RegionSettings, BannedFromRegion
from pages.models import Page, PageFile
from maps.models import MapData
from redirects.models import Redirect
from tags.models import Tag, PageTagSet

from .. utils import move_to_region


class MoveRegionTests(TestCase):
    def setUp(self):
        self.regions = []

        self.sf = Region(full_name="San Francisco", slug="sf")
        self.sf.save()
        self.oak = Region(full_name="Oakland", slug="oak")
        self.oak.save()

    def test_move_exists(self):
        ###########################################################
        # Moving a page that already exists should just silently
        # continue.
        ###########################################################

        p_sf = Page(region=self.sf)
        p_sf.content = "<p>Hello, world in SF.</p>"
        p_sf.name = "Page A"
        p_sf.save()

        p_oak = Page(region=self.oak)
        p_oak.content = "<p>Hello, world started on Oak.</p>"
        p_oak.name = "Page A"
        p_oak.save()

        move_to_region(self.sf, pages=[p_sf])
        # Shouldn't have been moved.
        p = Page.objects.filter(region=self.sf, name="Page A")[0]
        self.assertEqual(p.content, "<p>Hello, world in SF.</p>")

    def test_move_with_fks(self):
        ###########################################################
        # Moving should carry along files and FK'ed items that
        # point to it.
        ###########################################################

        p = Page(region=self.sf)
        p.content = "<p>A page with files and a map in SF.</p>"
        p.name = "Page With FKs"
        p.save()
        # Create a file that points at the page.
        pf = PageFile(file=ContentFile("foo"), name="file.txt", slug=p.slug, region=self.sf)
        pf.save()
        # Create a redirect that points at the page.
        redirect = Redirect(source="foobar", destination=p, region=self.sf)
        redirect.save()
        # Create a map that points at the page.
        points = GEOSGeometry("""MULTIPOINT (-122.4378964233400069 37.7971758820830033, -122.3929211425700032 37.7688207875790027, -122.3908612060599950 37.7883584775320003, -122.4056240844700056 37.8013807351830025, -122.4148937988299934 37.8002956347170027, -122.4183270263600036 37.8051784612779969)""")
        map = MapData(points=points, page=p, region=self.sf)
        map.save()
        # Add tags to page
        tagset = PageTagSet(page=p, region=self.sf)
        tagset.save()
        tag = Tag(name="tag1", region=self.sf)
        tag.save()
        tagset.tags.add(tag)

        move_to_region(self.oak, pages=[p])

        # Check to see that the related objects were moved.
        p = Page.objects.get(name="Page With FKs", region=self.oak)
        self.assertEqual(len(MapData.objects.filter(page=p, region=self.oak)), 1)
        self.assertEqual(len(p.pagetagset.tags.all()), 1)
        self.assertEqual(len(Redirect.objects.filter(destination=p, region=self.oak)), 1)
        self.assertEqual(len(PageFile.objects.filter(slug=p.slug, region=self.oak)), 1)

        # Check to see that version history was moved as well
        self.assertEquals(p.versions.all().count(), 1)
        self.assertEqual(len(MapData.versions.filter(page=p, region=self.oak)), 1)
        for pts in p.pagetagset.tags.all():
            self.assertEqual(pts.versions.all().count(), 1)
        self.assertEqual(len(Redirect.versions.filter(destination=p, region=self.oak)), 1)
        self.assertEqual(len(PageFile.versions.filter(slug=p.slug, region=self.oak)), 1)

        # ..and that the page is no longer in the SF region
        self.assertFalse(Page.objects.filter(region=self.sf, name="Page With FKs").exists())

    def test_move_with_existing_file(self):
        p = Page(region=self.sf)
        p.content = "<p>A page w a file.</p>"
        p.name = "Page With File"
        p.save()
        # Create a file that points at the page.
        pf_sf = PageFile(name="file.txt", slug=p.slug, region=self.sf)
        pf_sf.file.save("file.txt", ContentFile("foo sf"))
        pf_sf.save()

        # Make the file already exist on oak
        pf_oak = PageFile(name="file.txt", slug=p.slug, region=self.oak)
        pf_oak.file.save("file.txt", ContentFile("foo oak"))
        pf_oak.save()

        move_to_region(self.oak, pages=[p])

        # The file shouldn't have been moved because it already exists at the
        # destination.

        pf = PageFile.objects.get(slug=p.slug, region=self.oak)
        self.assertEqual(pf_oak.file.name, pf.file.name)

    def test_move_redirects(self):
        p = Page(region=self.sf)
        p.content = "<p>A page.</p>"
        p.name = "Page content"
        p.save()

        redir = Redirect(
            source="short name",
            destination=p,
            region=self.sf)
        redir.save()

        move_to_region(self.oak, pages=[p], redirects=[redir])

        # Redirect should be in Oak
        self.assertEqual(Redirect.objects.filter(region=self.oak).count(), 1)
        
    def test_move_redirect_destination(self):
        # Destination page should be transparently moved if not specified
        p = Page(region=self.sf)
        p.content = "<p>A page.</p>"
        p.name = "Page content not moved directly"
        p.save()

        redir = Redirect(
            source="short name",
            destination=p,
            region=self.sf)
        redir.save()

        move_to_region(self.oak, redirects=[redir])

        # Redirect should be in Oak
        self.assertEqual(Redirect.objects.filter(region=self.oak).count(), 1)
        # ..and page
        self.assertTrue(Page.objects.filter(slug='page content not moved directly', region=self.oak).exists())


class RegionPermissionTests(TestCase):
    def setUp(self):
        self.regions = []

        self.sf = Region(full_name="San Francisco", slug="sf")
        self.sf.save()
        self.oak = Region(full_name="Oakland", slug="oak")
        self.oak.save()

        self.philip = User(username="Philip", email="philip@example.org")
        self.philip.save()

        self.marina = User(username="Marina", email="marina@example.org")
        self.marina.save()

        # Philip admin of SF
        self.sf.regionsettings.admins.add(self.philip)

        # Marina admin of Oakland
        self.oak.regionsettings.admins.add(self.marina)

    def test_banned_cant_edit(self):
        # Add Marina to the SF banned list
        banned_sf, created = BannedFromRegion.objects.get_or_create(region=self.sf)
        banned_sf.users.add(self.marina)

        p = Page(name="In sf", region=self.sf)
        self.assertFalse(self.marina.has_perm('pages.change_page', p))

        mapdata = MapData(page=p, region=self.sf)
        self.assertFalse(self.marina.has_perm('maps.change_map', mapdata))

        redirect = Redirect(source="testsource", destination=p, region=self.sf)
        self.assertFalse(self.marina.has_perm('redirects.change_redirect', redirect))
