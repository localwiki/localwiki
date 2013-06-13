from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from models import Tag


class TagAdmin(GuardedModelAdmin):
    pass

admin.site.register(Tag, TagAdmin)
