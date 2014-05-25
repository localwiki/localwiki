from celery.task import task
from lxml.html import fragments_fromstring
import urllib
import urlparse

from django.utils.translation import ugettext as _
from django.db import models
from django.db.models.signals import post_save

from maps.models import MapData
from pages.models import Page
from pages.plugins import _files_url, file_url_to_name


class PageScore(models.Model):
    """
    A score assigned to a page that, roughly speaking, represents its
    quality.
    """
    page = models.OneToOneField(Page, related_name='score')
    score = models.SmallIntegerField()

    def __unicode__(self):
        return _("Page score %s: %s") % (self.page, self.score)

def is_internal(url):
    return (not urlparse.urlparse(url).netloc)

@task
def _calculate_page_score(page):
    score = 0
    num_images = 0
    link_num = 0

    # 1 point for having a map
    if MapData.objects.filter(page=page).exists():
        score += 1

    # Parse the page HTML and look for good stuff
    for e in fragments_fromstring(page.content):
        for i in e.iter('img'):
            src = i.attrib.get('src', '')
            if src.startswith(_files_url):
                num_images += 1
        for i in e.iter('a'):
            src = i.attrib.get('src', '')
            if is_internal(src):
                name = urllib.unquote(src)
                # Only count links to pages that exist
                if Page(name=name, region=page.region).exists():
                    link_num += 1

    # One point for each image, up to three points
    score += min(num_images, 3)

    # 1 point for the first internal link and 1 point if there's at least
    # two more links.
    if link_num >= 1:
        score += 1
    if link_num >= 3:
        score += 1
   
    score_obj = PageScore.objects.filter(page=page)
    if not score_obj.exists():
        score_obj = PageScore(page=page)
    else:
        score_obj = score_obj[0]
    score_obj.score = score
    score_obj.save()

def _handle_page_score(sender, instance, created, raw, **kws):
    if raw:
        return
    if sender == Page:
        _calculate_page_score.delay(instance)
    elif sender == MapData:
        _calculate_page_score.delay(instance.page)


post_save.connect(_handle_page_score)
