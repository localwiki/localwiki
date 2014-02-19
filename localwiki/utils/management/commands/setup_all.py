from django.core.management.base import BaseCommand
from django.core.management import call_command


def has_regions():
    from regions.models import Region
    return Region.objects.exists()


class Command(BaseCommand):
    help = ('Sets up the localwiki install.  '
            'Only run this command on a fresh install.')

    def handle(self, *args, **options):
        call_command('syncdb', interactive=False, verbosity=0)
        call_command('migrate', autofake_first=True, verbosity=0)
        call_command('collectstatic', interactive=False, verbosity=0)
        call_command('reset_permissions', verbosity=0)

        if not has_regions():
            print "Adding main region.."
            call_command('loaddata', 'initial_regions')
