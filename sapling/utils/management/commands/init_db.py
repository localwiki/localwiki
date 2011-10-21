import os
import subprocess
import string
from random import choice
import tempfile

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = ('Creates a DB user, DB name, and strong, random DB password.  '
            'Also creates a spatial DB template if needed.')

    def _is_debian(self):
        if not os.path.exists('/etc/issue'):
            return False
        f = open('/etc/issue')
        info = f.read().lower()
        return info.startswith('debian') or info.startswith('ubuntu')

    def create_spatial_template(self):
        if self._is_debian():
            script = 'create_template_postgis-debian.sh'
        else:
            which_pgis = raw_input(
"""Which version of PostGIS are you running?:\n
   1) PostGIS 1.5
   2) PostGIS 1.4
   3) PostGIS 1.3

Enter "1", "2" or "3".\n""").strip().strip('"')[0]
            if which_pgis == '1':
                script = 'create_template_postgis-1.5.sh'
            elif which_pgis == '2':
                script = 'create_template_postgis-1.4.sh'
            elif which_pgis == '3':
                script = 'create_template_postgis-1.3.sh'

        script_path = os.path.join(settings.PROJECT_ROOT,
            'install_config', 'postgis_template_scripts', script)
        # Make a temp file so postgres user can always read it.
        fd, temp_path = tempfile.mkstemp()
        f = os.fdopen(fd, 'w')
        script_content = open(script_path).read()
        f.write(script_content)
        f.close()
        # Make the temp script executable.
        os.chmod(temp_path, 0775)

        p = subprocess.Popen('sudo -u postgres %s' % temp_path,
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        
        # Print the script output.
        for line in p.stdout:
            if line.strip():
                print line.strip()

    def gen_password(self):
        chars = string.letters + string.digits
        length = 30
        return ''.join(choice(chars) for _ in range(length))

    def create_db(self):
        default_username = 'localwiki'
        default_dbname = 'localwiki'

        rand_password = self.gen_password()
        # First, let's try and create the default username.
        username = default_username
        p = subprocess.Popen("""sudo -u postgres psql -d template1 """
            """-c "CREATE USER %s WITH PASSWORD '%s'" """ % (username, rand_password),
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        print retval
        if retval != 0:
            # Oops, default name already taken.  This is probably their
            # second install on the same system.  Let's prompt for a new
            # username.
            print ("Default DB username '%s' already taken. "
                   "Enter new DB username:" % default_username)
            username = raw_input().strip()
            p = subprocess.Popen("""sudo -u postgres psql -d template1 """
                """-c "CREATE USER %s WITH PASSWORD '%s'" """ % (username, rand_password),
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()
            for line in p.stdout:
                if line.strip():
                    print line.strip()

        # Now let's try and create the default database.
        dbname = default_dbname
        p = subprocess.Popen('sudo -u postgres createdb -E UTF8 -T template_postgis -O %s %s' % (username, dbname),
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        if retval != 0:
            # Oops, db already exists.  This is probably their second
            # install on the same system.  Let's prompt for a new
            # database name.
            print ("Default DB name '%s' already taken. "
                   "Enter new DB name:" % default_dbname)
            dbname = raw_input().strip()
            p = subprocess.Popen('sudo -u postgres createdb -E UTF8 -T template_postgis -O %s %s' % (username, dbname),
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()
            for line in p.stdout:
                if line.strip():
                    print line.strip()
            if retval != 0:
                print "Error creating database"
                return

        self.dbname = dbname
        self.username = username
        self.password = rand_password
        print "Database '%s' with username '%s' created!" % (dbname, username)

    def update_settings(self):
        localsettings = open(os.path.join(settings.DATA_ROOT, 'conf',
            'localsettings.py')).read()
        localsettings = localsettings.replace('DBNAMEHERE', self.dbname)
        localsettings = localsettings.replace('DBUSERNAMEHERE', self.username)
        localsettings = localsettings.replace('DBPASSWORDHERE', self.password)
        f = open(os.path.join(settings.DATA_ROOT, 'conf',
            'localsettings.py'), 'w')
        f.write(localsettings)
        f.close()

    def handle(self, *args, **options):
        self.create_spatial_template()
        self.create_db()
        self.update_settings()
