from localwiki.utils.urlresolvers import reverse


class ActivityForModel(object):
    """
    Subclass this class and then register your subclass with
    activity.register() for your model to appear on the Activity pages.

    Loosely modeled after the Django syndication feed framework.
    """
    classname = None
    page_slug_attribute_name = None

    def __init__(self, region=None):
        self.region = region

    def queryset(self, start_at=None):
        """
        Returns:
            A queryset of historical instances that make up the recent
            changes of your model.

        Args:
            start_at: A datetime that the queryset is expected to start at.
                      Can also be None.
        """
        pass

    def page(self, obj):
        """
        Args:
            obj: The historical instance, taken from your queryset(),
                 that we are displaying on the Activity page.

        Returns:
            The page object associated with obj.
        """
        return obj.page

    def get_page_lookup_info(self):
        if self.classname == 'page':
            return 'slug'

        if self.page_slug_attribute_name:
            return self.page_slug_attribute_name

        # Try and find attribute
        m = self.queryset().model
        if hasattr(m, 'page'):
            return 'page__slug'
        # Create instance of class to get attribute here
        if hasattr(m(), 'slug'):
            return 'slug'

    def title(self, obj):
        """
        Args:
            obj: The historical instance, taken from queryset(),
                 that we are displaying on the Activity page.

        Returns:
            The title of this object.
        """
        return obj.name

    def diff_url(self, obj):
        """
        args:
            obj: the historical instance, taken from your queryset(),
                 that we are displaying on the Activity page.

        returns:
            the diff url associated with obj.
        """
        return reverse('%s:compare-dates' % obj._meta.app_label, kwargs={
            'slug': self.page(obj).pretty_slug,
            'region': self.page(obj).region.slug,
            'date1': obj.version_info.date,
        })

    def as_of_url(self, obj):
        """
        args:
            obj: the historical instance, taken from your queryset(),
                 that we are displaying on the Activity page.

        returns:
            the url to display the version of the obj specified.
        """
        return reverse('%s:as_of_date' % obj._meta.app_label, kwargs={
            'slug': self.page(obj).pretty_slug,
            'region': self.page(obj).region.slug,
            'date': obj.version_info.date,
        })
