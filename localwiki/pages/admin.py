from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from models import Page, PageFile


def page_link(page):
    """Public link to the page"""
    link = page.get_absolute_url()
    return ('<a target="_blank" href="%s">'
            '<img src="/media/img/icons/link_external.png"> View</a><br/>' %
            link)

page_link.allow_tags = True
page_link.short_description = "Public"


class PageAdmin(GuardedModelAdmin):
    readonly_fields = ('name', 'content')
    list_display = ('id', 'name', 'slug', page_link)
    list_display_links = ('name', 'slug')
    search_fields = ('name', 'slug')


admin.site.register(Page, PageAdmin)
admin.site.register(PageFile, GuardedModelAdmin)
