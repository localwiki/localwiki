from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db.utils import IntegrityError
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = ('Sets the email address of the specified username.\n'+
           'Usage: localwiki-manage set_email <username> <email address>')

    def handle(self, user_name=None, email_address="", **options):
        if user_name is None:
            raise CommandError("You must provide a username.")

        try:
            uname = User.objects.get(username=user_name)
        except User.DoesNotExist:
            raise CommandError('Username "%s" does not exist.' % user_name)
        
        uname.email = email_address
        
        try:
            uname.save()
        except IntegrityError:
            raise CommandError('That email address is already in use by '+
                               'another user. You must specify a unique '+
                               'email address.')
        
        self.stdout.write('Successfully set email address for "%s" to "%s".\n' % (
                              user_name, email_address))
