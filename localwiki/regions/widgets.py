from tags.widgets import TagEdit


class UserEdit(TagEdit):
    def autocomplete_url(self):
        return ('/_api/users/suggest/%s' % self.region.slug)
