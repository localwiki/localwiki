from django.contrib.auth.models import User

from follow.utils import register as register_follow
from follow.models import Follow

from versionutils import versioning 
from regions.models import Region
from pages.models import Page


# Register models with follow app
register_follow(User)
register_follow(Page)
register_follow(Region)

# Version the Follow model
versioning.register(Follow)

# Fire signals
import signals
