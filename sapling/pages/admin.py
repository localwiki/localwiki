from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from models import Page


class PageAdmin(GuardedModelAdmin):
    pass


admin.site.register(Page, PageAdmin)
