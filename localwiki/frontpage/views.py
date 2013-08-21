import base64
from mimetypes import guess_extension

from django.views.generic import View 
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.core.files.base import ContentFile

from pages.views import PageDetailView
from pages.models import Page
from regions.views import RegionMixin
from regions.views import TemplateView

from models import FrontPage
from forms import CoverPhotoForm


class FrontPageView(TemplateView):
    template_name = 'frontpage/base.html'

    def get_context_data(self, *args, **kwargs):
        context = super(FrontPageView, self).get_context_data() 
        # So that the Page can be edited if they want to replace
        # the auto-generated Front Page.
        context['frontpage'] = FrontPage.objects.get(region=self.get_region())
        context['random_pages'] = Page.objects.filter(region=self.get_region()).order_by('?')[:30]
        context['page'] = Page(name="Front Page", region=self.get_region())
        return context


class CoverUploadView(RegionMixin, View):
    def post(self, *args, **kwargs):
        # Convert data URI into a ContentFile
        data_uri = self.request.POST.get('coverphoto[cropped]')
        metadata, encoded_photo = data_uri.split(',')
        mimetype, encoding = metadata.split(';')
        mimetype = mimetype.split(':')[1]
        extension = guess_extension(mimetype)
        filename = 'coverphoto%s' % extension
        photo = ContentFile(base64.decodestring(encoded_photo), name=filename)

        frontpage = FrontPage.objects.get(region=self.get_region())
        frontpage.cover_photo = photo
        frontpage.save()
        messages.add_message(self.request, messages.SUCCESS, _("Cover photo updated!"))
                
        return HttpResponseRedirect(
            reverse('frontpage', kwargs={'region': self.get_region().slug}))
