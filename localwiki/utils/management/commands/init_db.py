import os
import subprocess
import string
from random import choice
import tempfile


class Command(object):
    """
    Creates a DB user, DB name, and strong, random DB password.
    Also creates a spatial DB template if needed.
    """
    def check_postgres_user(self):
        """
        Does the system have a `postgres` user?
        """
        try:
            subprocess.check_call("id postgres", shell=True, 
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            self.has_postgres_user = False
        else:
            self.has_postgres_user = True

    def _as_postgres_user(self):
        if self._is_os_x():
            # OS X doesn't have a postgres user, at least for homebrew installs.
            # So let's just use the default system user.
            return ''
        if self.has_postgres_user:
            return 'sudo -u postgres'
        return ''

    def _is_debian(self):
        if not os.path.exists('/etc/issue'):
            return False
        f = open('/etc/issue')
        info = f.read().lower()
        if info.startswith('debian') or info.startswith('ubuntu'):
            return True

        if os.path.exists('/etc/lsb-release'):
            f = open('/etc/lsb-release')
            info = f.read().lower()
            if 'distrib_id=ubuntu' in info:
                return True
            if 'distrib_id=debian' in info:
                return True

        return False

    def _is_os_x(self):
        import platform
        return platform.platform().startswith('Darwin')

    def create_spatial_template(self):
        if self._is_debian():
            script = 'create_template_postgis-debian.sh'
        elif self._is_os_x():
            script = 'create_template_postgis-os_x.sh'
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

        script_path = os.path.join(self.PROJECT_ROOT, 'etc',
            'install_config', 'postgis_template_scripts', script)
        # Make a temp file so postgres user can always read it.
        fd, temp_path = tempfile.mkstemp()
        f = os.fdopen(fd, 'w')
        script_content = open(script_path).read()
        f.write(script_content)
        f.close()
        # Make the temp script executable.
        os.chmod(temp_path, 0775)

        p = subprocess.Popen(self._as_postgres_user() + (' %s' % temp_path),
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        if retval != 0:
            for line in p.stdout:
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
        p = subprocess.Popen(self._as_postgres_user() +
            """ psql -d template1 -c "CREATE USER %s WITH PASSWORD '%s'" """
            % (username, rand_password),
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        if retval != 0:
            for line in p.stdout:
                print line.strip()
            # Oops, default name already taken.  This is probably their
            # second install on the same system.  Let's prompt for a new
            # username.
            print ("Default DB username '%s' already taken. "
                   "Enter new DB username:" % default_username)
            username = raw_input().strip()
            p = subprocess.Popen(self._as_postgres_user() +
                """ psql -d template1 -c "CREATE USER %s WITH PASSWORD '%s'" """
                % (username, rand_password),
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()
            for line in p.stdout:
                if line.strip():
                    print line.strip()

        # Now let's try and create the default database.'
        dbname = default_dbname
        p = subprocess.Popen(self._as_postgres_user() +
                """ createdb -E UTF8 -T template_postgis -O %s %s""" %
                (username, dbname),
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        if retval != 0:
            for line in p.stdout:
                print line.strip()
            # Oops, db already exists.  This is probably their second
            # install on the same system.  Let's prompt for a new
            # database name.
            print ("Default DB name '%s' already taken. "
                   "Enter new DB name:" % default_dbname)
            dbname = raw_input().strip()
            p = subprocess.Popen(self._as_postgres_user() +
                """ createdb -E UTF8 -T template_postgis -O %s %s""" %
                (username, dbname),
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
        localsettings = open(os.path.join(self.DATA_ROOT, 'conf',
            'localsettings.py')).read()
        localsettings = localsettings.replace('DBNAMEHERE', self.dbname)
        localsettings = localsettings.replace('DBUSERNAMEHERE', self.username)
        localsettings = localsettings.replace('DBPASSWORDHERE', self.password)
        f = open(os.path.join(self.DATA_ROOT, 'conf',
            'localsettings.py'), 'w')
        f.write(localsettings)
        f.close()

    def handle(self, *args, **options):
        self.check_postgres_user()
        self.create_spatial_template()
        self.create_db()
        self.update_settings()


def run(DATA_ROOT=None, PROJECT_ROOT=None):
    c = Command()
    c.DATA_ROOT = DATA_ROOT
    c.PROJECT_ROOT = PROJECT_ROOT
    c.handle()
