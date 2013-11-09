from django.contrib.auth.models import User

from tags.forms import TagSetField

from widgets import UserEdit


# We re-use the tag set field here, because it's the kind of
# behavior we want.
class UserSetField(TagSetField):
    model = User
    name_attribute = 'username'
    widget = UserEdit()

    def get_queryset(self):
        return User.objects.all()

    def get_or_create_tag(self, word):
        return User.objects.get(username__iexact=word)
