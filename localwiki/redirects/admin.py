from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from models import Redirect


class RedirectAdmin(GuardedModelAdmin):
    pass

admin.site.register(Redirect, RedirectAdmin)
