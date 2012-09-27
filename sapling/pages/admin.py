from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from models import Page


class PageAdmin(GuardedModelAdmin):
    readonly_fields = ('name', 'content')


admin.site.register(Page, PageAdmin)
