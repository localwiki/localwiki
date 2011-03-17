from django.contrib import admin

from olwidget.admin import GeoModelAdmin

from models import *

admin.site.register(MapData, GeoModelAdmin)
