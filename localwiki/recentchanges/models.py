from django.core.urlresolvers import reverse


class RecentChanges(object):
    """
    Subclass this class and then register your subclass with
    recentchanges.register() for your model to appear on Recent Changes.

    Loosely modeled after the Django syndication feed framework.
    """
    classname = None

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
                 that we are displaying on Recent Changes.

        Returns:
            The page object associated with obj.
        """
        return obj.page

    def title(self, obj):
        """
        Args:
            obj: The historical instance, taken from queryset(),
                 that we are displaying on Recent Changes.

        Returns:
            The title of this object.
        """
        return obj.name

    def diff_url(self, obj):
        """
        args:
            obj: the historical instance, taken from your queryset(),
                 that we are displaying on recent changes.

        returns:
            the diff url associated with obj.
        """
        return reverse('%s:compare-dates' % obj._meta.app_label, kwargs={
            'slug': self.page(obj).pretty_slug,
            'date1': obj.version_info.date,
        })

    def as_of_url(self, obj):
        """
        args:
            obj: the historical instance, taken from your queryset(),
                 that we are displaying on recent changes.

        returns:
            the url to display the version of the obj specified.
        """
        return reverse('%s:as_of_date' % obj._meta.app_label, kwargs={
            'slug': self.page(obj).pretty_slug,
            'date': obj.version_info.date,
        })
