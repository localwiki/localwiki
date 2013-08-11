from django.contrib.auth.models import User
from django.views.generic import RedirectView

from regions.models import Region
from regions import get_main_region
from pages.models import Page


class UserPageView(RedirectView):
    permanent = False
    query_string = True

    def get_redirect_url(self, **kwargs):
        username = self.kwargs.get('username')
        user = User.objects.get(username=username)
        pagename = "Users/%s" % username
        user_pages = Page.objects.filter(name=pagename)
        if user_pages:
            # Has a userpage in a region
            user_page = user_pages[0]
        else:
            # Check to see if they've edited a region recently
            edited_pages = Page.versions.filter(version_info__user=user)
            if edited_pages:
                region = edited_pages[0].region
                user_page = Page(name=pagename, region=region)
            else:
                user_page = Page(name=pagename, region=get_main_region())
        return user_page.get_absolute_url()
