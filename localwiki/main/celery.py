from __future__ import absolute_import
import os

from django.conf import settings

from celery import Celery
from celery._state import set_default_app

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

app = Celery('main', set_as_current=True)
set_default_app(app)
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(settings.INSTALLED_APPS, related_name='tasks')
