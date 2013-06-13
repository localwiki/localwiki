from django.conf import settings


def license_agreements(context):
    return {
        'GLOBAL_LICENSE_NOTE': settings.GLOBAL_LICENSE_NOTE,
        'EDIT_LICENSE_NOTE': settings.EDIT_LICENSE_NOTE,
        'SIGNUP_TOS': settings.SIGNUP_TOS,
    }
