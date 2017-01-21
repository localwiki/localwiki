from django.conf import settings


class LicenseMixin(object):
    license_agreement = settings.EDIT_LICENSE_NOTE
