from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from models import Region, RegionSettings


class RegionAdmin(GuardedModelAdmin):
    pass


class RegionSettingsAdmin(GuardedModelAdmin):
    pass

admin.site.register(Region, RegionAdmin)
admin.site.register(RegionSettings, RegionSettingsAdmin)
