from django.conf import settings

from models import Region
import site


def get_main_region():
    return Region.objects.get(slug=settings.MAIN_REGION)
