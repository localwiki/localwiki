from django.core.management.base import BaseCommand
from django.core.management import call_command


def has_pages():
    from pages.models import Page
    return Page.objects.exists()


class Command(BaseCommand):
    help = ('Sets up the localwiki install.  '
            'Only run this command on a fresh install.')

    def handle(self, *args, **options):
        call_command('syncdb', verbosity=0)
        call_command('migrate', verbosity=0)
        call_command('collectstatic', interactive=False, verbosity=0)
        call_command('reset_permissions', verbosity=0)

        if not has_pages():
            print "Adding basic pages.."
            call_command('loaddata', 'basic_pages')
