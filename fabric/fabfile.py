import os
import sys
import random
import string
from contextlib import contextmanager as _contextmanager
from fabric.api import *
from fabric.contrib.files import upload_template, exists
from fabric.network import disconnect_all
from ilogue import fexpect

####################################################################
#  Ignore the `secrets_path` for development usage.
#
#  For production deployments, you'll want to set up the
#  `secrets_path` as follows:
#    1. Copy config_secrets.example/ (found in this dir) somewhere.
#    2. Edit it with your secret values.
#  
#  You can provision without setting up these secrets, but this will
#  allow you to e.g. have SSL, Sentry, and other stuff as we add it.
####################################################################
env.secrets_path = '/Users/philip/projects/localwiki/config_secrets/'

try:
    sys.path.append(env.secrets_path)
    import secrets as config_secrets
except ImportError:
    sys.path.append(os.path.abspath('config_secrets.example'))
    import secrets as config_secrets

env.host_type = None

########################
# Defaults             #
########################

env.localwiki_root = '/srv/localwiki'
env.src_root = os.path.join(env.localwiki_root, 'src')
env.virtualenv = os.path.join(env.localwiki_root, 'env')
env.data_root = os.path.join(env.virtualenv, 'share', 'localwiki')
env.apache_settings = {
    'server_name': 'localwiki.net',
    'server_admin': 'contact@localwiki.org',
}
env.sentry_key = config_secrets.sentry_key
 
def vagrant():
    env.host_type = 'vagrant'
    env.user = 'vagrant'
    # connect to the port-forwarded ssh
    env.hosts = ['127.0.0.1:2222']
 
    # We assume the vagrant vm is in the 'vagrant' directory
    # inside of this directory. If not, symlink it here.
    with lcd('vagrant'):
        # use vagrant ssh key
        result = local('vagrant ssh-config | grep IdentityFile', capture=True)
    env.key_filename = result.split()[1].strip('"')

@_contextmanager
def virtualenv():
    with prefix('source %s/bin/activate' % env.virtualenv):
        yield

def setup_jetty():
    sudo("sed -i 's/NO_START=1/NO_START=0/g' /etc/default/jetty")
    sudo("cp /etc/solr/conf/schema.xml /etc/solr/conf/schema.xml.orig")
    put("config/solr_schema.xml", "/etc/solr/conf/schema.xml", use_sudo=True)
    put("config/daisydiff.war", "/var/lib/jetty/webapps", use_sudo=True)
    sudo("service jetty stop")
    sudo("service jetty start")

def install_system_requirements():
    # Update package list
    sudo('apt-get update')
    sudo('apt-get -y install python-software-properties')

    # Need GDAL >= 1.10 and PostGIS 2, so we use this
    # PPA.
    sudo('apt-add-repository -y ppa:ubuntugis/ubuntugis-unstable')
    sudo('apt-get update')

    # Ubuntu system packages
    system_python_pkg = [
        'python-setuptools',
        'python-lxml',
        'python-imaging',
        'python-psycopg2',
        'python-pip',
        'git'
    ]
    solr_pkg = ['solr-jetty', 'default-jre-headless']
    apache_pkg = ['apache2', 'libapache2-mod-wsgi']
    postgres_pkg = ['gdal-bin', 'proj', 'postgresql-9.1-postgis-2.0']
    memcached_pkg = ['memcached']
    varnish_pkg = ['varnish']
    packages = (
        system_python_pkg +
        solr_pkg +
        apache_pkg +
        postgres_pkg +
        memcached_pkg +
        varnish_pkg
    )
    sudo('DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes install %s' % ' '.join(packages))

def init_postgres():
    # Generate a random password, for now.
    env.postgres_db_pass = ''.join([random.choice(string.letters + string.digits) for i in range(40)])
    sudo("""psql -d template1 -c "CREATE USER localwiki WITH PASSWORD '%s'" """ % env.postgres_db_pass, user='postgres')
    sudo("""psql -d template1 -c "ALTER USER localwiki CREATEDB" """, user='postgres')
    sudo("createdb -E UTF8 -O localwiki localwiki", user='postgres')
    # Init PostGIS
    sudo('psql -d localwiki -c "CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology;"', user='postgres')

def init_localwiki_install():
    # Update to latest virtualenv
    sudo('pip install --upgrade virtualenv')

    # Create virtualenv
    run('virtualenv --system-site-packages %s' % env.virtualenv)

    with virtualenv():
        with cd(env.src_root):
            # Install core localwiki module as well as python dependencies
            run('python setup.py develop')

            init_postgres()

            # Set up the default media, static, conf, etc directories
            run('mkdir -p %s/share' % env.virtualenv)
            put('config/defaults/localwiki', os.path.join(env.virtualenv, 'share'))

            # Install Django settings template
            env.django_secret_key = ''.join([
                random.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)')
                for i in range(50)
            ])
            upload_template('config/localsettings.py', os.path.join(env.virtualenv, 'share', 'localwiki', 'conf'),
                context=env, use_jinja=True)

            run('localwiki-manage setup_all')

def setup_repo():
    sudo('mkdir -p %s' % env.localwiki_root)
    sudo('chown -R %s.%s %s' % (env.user, env.user, env.localwiki_root))
    if not exists(env.src_root):
        run('git clone https://github.com/localwiki/localwiki.git %s' % env.src_root)
    # XXX TODO temporary
    switch_branch('hub_fabric_deploy_needed')

def switch_branch(branch):
    with cd(env.src_root):
        run('git checkout %s' % branch)

def install_ssl_certs():
    # Install our SSL certs for apache
    sudo('mkdir -p /etc/apache2/ssl')
    sudo('chown -R www-data:www-data /etc/apache2/ssl')
    sudo('chmod 700 /etc/apache2/ssl')
    with settings(warn_only=True):
        put(os.path.join(env.secrets_path, 'ssl') + '/*', '/etc/apache2/ssl/', use_sudo=True)

def setup_apache():
    with settings(hide('warnings', 'stdout', 'stderr')):
        # Enable mod_wsgi, mod_headers, mod_rewrite
        sudo('a2enmod wsgi')
        sudo('a2enmod headers')
        sudo('a2enmod rewrite')
        sudo('a2enmod proxy')
        sudo('a2enmod ssl')

        # Install localwiki.wsgi
        upload_template('config/localwiki.wsgi', os.path.join(env.localwiki_root),
            context=env, use_jinja=True)

        # Allow apache to save uploads, etc
        sudo('chown www-data:www-data %s' % os.path.join(env.localwiki_root))

        # Disable default apache site
        if exists('/etc/apache2/sites-enabled/000-default'):
           sudo('a2dissite default')

        # Install apache config
        upload_template('config/apache/localwiki', '/etc/apache2/sites-available/localwiki',
            context=env, use_jinja=True, use_sudo=True)
        sudo('a2ensite localwiki')

        install_ssl_certs()
        
        # Restart apache
        sudo('service apache2 restart')

def setup_permissions():
    # Add the user we run commands with to the apache user group
    sudo('usermod -a -G www-data %s' % env.user)

def setup_mapserver():
    """
    Enable map-a.localwiki.org, map-b.localwiki.org, map-c.localwiki.org as
    cached proxies to cloudmade tiles.
    """
    setup_varnish()
    put('config/apache/map', '/etc/apache2/sites-available/map', use_sudo=True)
    sudo('a2ensite map')
    sudo('service apache2 restart')

def setup_varnish():
    put('config/varnish/default.vcl', '/etc/varnish/default.vcl', use_sudo=True)
    sudo('service varnish restart')

def add_ssh_keys():
    run('mkdir -p ~/.ssh && chmod 700 ~/.ssh')
    run('touch ~/.ssh/authorized_keys')
    run('mkdir ssh_to_add')
    put(os.path.join(env.secrets_path, 'ssh') + '/*', 'ssh_to_add/')
    run('cat ~/ssh_to_add/* >> ~/.ssh/authorized_keys')
    run('rm -rf ~/ssh_to_add')

def provision():
    if env.host_type == 'vagrant':
        fix_locale()

    add_ssh_keys()
    install_system_requirements()
    setup_permissions() 
    setup_jetty()
    setup_repo()
    init_localwiki_install()
    setup_apache()

    setup_mapserver()

def run_tests():
    # Must be superuser to run tests b/c of PostGIS requirement? Ugh..
    # XXX TODO: Fix this, somehow.  django-nose + pre-created test db?
    sudo("""psql -d postgres -c "ALTER ROLE localwiki SUPERUSER" """, user='postgres')
    with virtualenv():
        run('localwiki-manage test regions pages maps tags versioning diff ckeditor redirects users')
    sudo("""psql -d postgres -c "ALTER ROLE localwiki NOSUPERUSER" """, user='postgres')

def fix_locale():
    sudo('update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8')
    disconnect_all()
