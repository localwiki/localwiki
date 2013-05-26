from django.conf import settings


def license_agreements(context):
    return {
        'GLOBAL_LICENSE_NOTE': settings.GLOBAL_LICENSE_NOTE,
        'EDIT_LICENSE_NOTE': settings.EDIT_LICENSE_NOTE,
        'SIGNUP_TOS': settings.SIGNUP_TOS,
    }


def services(context):
    return {
        'GOOGLE_ANALYTICS_ID': getattr(settings, 'GOOGLE_ANALYTICS_ID', ''),
        'GOOGLE_ANALYTICS_SUBDOMAINS': getattr(settings, 'GOOGLE_ANALYTICS_SUBDOMAINS', ''),
        'GOOGLE_ANALYTICS_MULTIPLE_TOPLEVEL_DOMAINS': getattr(settings, 'GOOGLE_ANALYTICS_MULTIPLE_TOPLEVEL_DOMAINS', False)
    }
