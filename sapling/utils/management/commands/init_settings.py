import os
from random import choice


class Command(object):
    """
    Asks questions to auto-populate the local settings.
    """

    def _write_settings(self, vals):
        localsettings = open(os.path.join(self.DATA_ROOT, 'conf',
            'localsettings.py')).read()
        for k, v in vals.iteritems():
            localsettings = localsettings.replace(k, v)

        f = open(os.path.join(self.DATA_ROOT, 'conf',
            'localsettings.py'), 'w')
        f.write(localsettings)
        f.close()

    def _generate_secret_key(self):
        """
        Generate a local secret key.
        """
        secret_key = ''.join([
            choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)')
            for i in range(50)
        ])
        return secret_key

    def handle(self, *args, **options):
        print 'Get a Cloudmade API Key.'
        print '1. Go to http://cloudmade.com/register'
        print ('2. After you\'ve signed in, click "Get an API Key". '
               'Fill out the form (details don\'t matter)')
        print '3. Paste the API key below:'
        cloudmade_api_key = raw_input().strip()

        self._write_settings({
            'CLOUDMADEAPIKEYHERE': cloudmade_api_key,
            'SECRETKEYHERE': self._generate_secret_key(),
        })


def run(DATA_ROOT=None, PROJECT_ROOT=None):
    c = Command()
    c.DATA_ROOT = DATA_ROOT
    c.PROJECT_ROOT = PROJECT_ROOT
    c.handle()
