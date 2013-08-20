from regions.views import TemplateView

from pages.views import PageDetailView
from pages.models import Page


class FrontPageView(TemplateView):
    template_name = 'frontpage/base.html'

    def get_context_data(self, *args, **kwargs):
        context = super(FrontPageView, self).get_context_data() 
        # So that the Page can be edited if they want to replace
        # the auto-generated Front Page.
        context['random_pages'] = Page.objects.filter(region=self.get_region()).order_by('?')[:30]
        context['page'] = Page(name="Front Page", region=self.get_region())
        return context
    


#url(r'^(?P<region>[^/]+?)/*$', slugify(PageDetailView.as_view()),
    #    kwargs={'slug': 'Front Page'}, name='frontpage'),
