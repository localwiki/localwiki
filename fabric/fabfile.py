"""
This is the main management script for provisioning and managing the LocalWiki servers.

==== Do this first ====

* Install vagrant >= 1.3.3
$ virtualenv env
$ source env/bin/activate
$ pip install -r requirements.txt

==== For development ====

This script will get you up and running with a development instance of the
LocalWiki servers.  Set up the requirements (above), then::

    $ mkdir vagrant_localwiki
    $ mv localwiki vagrant_localwiki  # Move repository inside
    $ cd vagrant_localwiki
    $ ln -s localwiki/vagrant/Vagrantfile .
    $ vagrant up  # Create and run vagrant instance
    $ cd localwiki/fabric/
    $ fab vagrant setup_dev  # Provision and set up for vagrant:

You now have a complete vagrant setup with the LocalWiki servers
running inside it.  To do development, you'll want to do something
like::

    $ cd vagrant_localwiki
    $ vagrant ssh

Then, when ssh'ed into vagrant::

    $ source /srv/localwiki/env/bin/activate
    $ localwiki-manage runserver --settings=main.settings.debug 0.0.0.0:8000

You can then access the development server at http://127.0.0.1:8082
on your local machine.  Hack on the code that lives inside of
vagrant_localwiki/localwiki.

Apache, which runs the production-style setup, will be accessible at
http://127.0.0.1:8081, but you should use :8082, the development server,
for most active work as it will automatically refresh.

To test a full production-style deploy in vagrant::

    $ cd localwiki/fabric
    $ fab vagrant deploy:local=True

Then visit the production server, http://127.0.0.1:8081, on your
local machine.  The 'deploy:local' flag tells us to use your local
code rather than a fresh git checkout.

==== EC2 ====

To provision a new EC2 instance::

    $ fab create_ec2 provision

==== Deploying to production ====

After provisioning, make sure you edit `roledefs` below to point
to the correct hosts. Then::

    $ fab production deploy

"""

import os
import sys
import random
import time
import shutil
import json
import string
from collections import defaultdict
from contextlib import contextmanager as _contextmanager
from fabric.api import *
from fabric.contrib.files import upload_template, exists
from fabric.network import disconnect_all
import boto.ec2
from ilogue import fexpect

####################################################################
#  Ignore `config_secrets` for development usage.
#
#  For production deployments, you'll want to:
#    1. cp config_secrets.example/ to config_secrets/
#    2. Edit the secrets.json and other files accordingly.
#  
#  You can provision without setting up these secrets, but this will
#  allow you to e.g. have SSL, Sentry, and other stuff as we add it.
####################################################################

####################################################################
# You'll want to edit this after provisioning:
####################################################################

roledefs = {
    'web': ['ubuntu@localwiki.net'],
}


def get_ec2_ami(region):
    # From http://cloud-images.ubuntu.com/releases/precise/release/

    # These are 64-bit, EBS-root-volume instances running
    # Ubuntu 12.04 LTS.
    images = {
        'us-west-1': 'ami-ecd8efa9',
        'us-west-2': 'ami-30079e00',
        'us-east-1': 'ami-69f5a900',
        # ..add others here if you wish
    }
    return images[region]

####################################################################
# Notes to self:
#
# After creating an EC2 instance, may want to create an IP:
#
# ec2-allocate-address
# ec2-associate-address -i <instance id> <ip address>
# 
# and set up a reverse DNS:
# https://portal.aws.amazon.com/gp/aws/html-forms-controller/contactus/ec2-email-limit-rdns-request
#
####################################################################


def get_config_secrets():
    # Set up config secrets
    if not os.path.exists('config_secrets'):
        shutil.copytree('config_secrets.example', 'config_secrets')    
    d = defaultdict(lambda : None)
    d.update(json.load(open('config_secrets/secrets.json')))
    return d

def save_config_secrets():
    f = open('config_secrets/secrets.json', 'w')
    json.dump(config_secrets, f, indent=4)
    f.close()

config_secrets = get_config_secrets()
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
env.sentry_key = config_secrets['sentry_key']
env.branch = 'hub'

def production():
    # Use the global roledefs
    env.roledefs = roledefs
    if not env.roles:
        env.roles = ['web']
    env.host_type = 'production'
 
def vagrant():
    # connect to the port-forwarded ssh
    env.roledefs = {
        'web': ['vagrant@127.0.0.1:2222']
    }
    if not env.roles:
        env.roles = ['web']
    env.host_type = 'vagrant'
    # We assume that this fabfile is inside of the vagrant
    # directory, two subdirectories deep.  See dev HOWTO
    # in main docstring.
    with lcd('../../'):
        # use vagrant ssh key
        result = local('vagrant ssh-config | grep IdentityFile', capture=True)
    env.key_filename = result.split()[1].strip('"')

def ec2():
    env.host_type = 'ec2'
    env.user = 'ubuntu'

    env.aws_access_key_id = config_secrets['aws_access_key_id']
    env.aws_secret_access_key = config_secrets['aws_secret_access_key']
    env.ec2_region = config_secrets['ec2_region']
    env.ec2_security_group = config_secrets['ec2_security_group']
    env.ec2_key_name = config_secrets['ec2_key_name']
    env.key_filename = config_secrets['ec2_key_filename']

def setup_dev():
    """
    Provision and set up for development on vagrant.
    """
    provision()
    # Use our vagrant shared directory instead of the
    # git checkout.
    sudo('rm -rf /srv/localwiki/src')
    sudo('ln -s /vagrant/localwiki /srv/localwiki/src', user='www-data')

def get_context(env):
    d = {}
    d.update(config_secrets)
    d.update(dict(env))
    return d

@_contextmanager
def virtualenv():
    with prefix('source %s/bin/activate' % env.virtualenv):
        yield

def setup_postgres(test_server=False):
    sudo('service postgresql stop')

    # Move the data directory to /srv/
    sudo('mkdir -p /srv/postgres')
    if not exists('/srv/postgres/data'):
        sudo('mv /var/lib/postgresql/9.1/main /srv/postgres/data')
    sudo('chown -R postgres:postgres /srv/postgres')

    # Add our custom configuration
    if not test_server:
        put('config/postgresql/postgresql.conf', '/etc/postgresql/9.1/main/postgresql.conf', use_sudo=True)
    else:
        put('config/postgresql/postgresql_test.conf', '/etc/postgresql/9.1/main/postgresql.conf', use_sudo=True)

    # Increase system shared memory limits
    shmmax = 288940032
    shmall = int(shmmax * 1.0 / 4096)
    sudo('echo "%s" > /proc/sys/kernel/shmmax' % shmmax)
    sudo('echo "%s" > /proc/sys/kernel/shmall' % shmall)
    sudo('echo "\nkernel.shmmax = %s\nkernel.shmall = %s" > /etc/sysctl.conf' % (shmmax, shmall))
    sudo('sysctl -p')

    sudo('service postgresql start')

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
    redis_pkg = ['redis-server']
    mailserver_pkg = ['postfix']
    packages = (
        system_python_pkg +
        solr_pkg +
        apache_pkg +
        postgres_pkg +
        memcached_pkg +
        varnish_pkg +
        redis_pkg + 
        mailserver_pkg
    )
    sudo('DEBIAN_FRONTEND=noninteractive apt-get -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" -y --force-yes install %s' % ' '.join(packages))

def init_postgres_db():
    # Generate a random password, for now.
    if not config_secrets['postgres_db_pass']:
        config_secrets['postgres_db_pass'] = ''.join([random.choice(string.letters + string.digits) for i in range(40)])
    sudo("""psql -d template1 -c "CREATE USER localwiki WITH PASSWORD '%s'" """ % config_secrets['postgres_db_pass'], user='postgres')
    sudo("""psql -d template1 -c "ALTER USER localwiki CREATEDB" """, user='postgres')
    sudo("createdb -E UTF8 -O localwiki localwiki", user='postgres')
    # Init PostGIS
    sudo('psql -d localwiki -c "CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology;"', user='postgres')

def update_django_settings():
    upload_template('config/localsettings.py',
        os.path.join(env.virtualenv, 'share', 'localwiki', 'conf'),
        context=get_context(env), use_jinja=True)

def init_localwiki_install():
    init_postgres_db()

    # Update to latest virtualenv
    sudo('pip install --upgrade virtualenv')

    # Create virtualenv
    run('virtualenv --system-site-packages %s' % env.virtualenv)

    with virtualenv():
        with cd(env.src_root):
            # Install core localwiki module as well as python dependencies
            run('python setup.py develop')

            # Set up the default media, static, conf, etc directories
            run('mkdir -p %s/share' % env.virtualenv)
            put('config/defaults/localwiki', os.path.join(env.virtualenv, 'share'))

            # Install Django settings template
            if not config_secrets['django_secret_key']:
                config_secrets['django_secret_key'] = ''.join([
                    random.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)')
                    for i in range(50)
                ])
            update_django_settings()

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
        put('config_secrets/ssl/*', '/etc/apache2/ssl/', use_sudo=True)

def get_ssl_info():
    """
    Figure out what the SSL info is based on what's in the ssl/ dir.
    """
    ssl_name = os.path.split(sudo('ls -d /etc/apache2/ssl/*').strip())[1]
    env.ssl_name = ssl_name
    ssl_files = sudo('ls /etc/apache2/ssl/%s' % ssl_name).split()
    crt = None
    key = None
    intermediate = None
    for fname in ssl_files:
        if fname.endswith('.crt') and fname != 'example.org.crt':
            crt = fname
        if fname.endswith('.key') and fname != 'example.org.key':
            key = fname
        if fname.endswith('intermediate.crt'):
            intermediate = fname
    env.ssl_key = key
    env.ssl_cert = crt
    env.ssl_intermediate = intermediate

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
            context=env, use_jinja=True, use_sudo=True)

        # Allow apache to save uploads, etc
        sudo('chown -R www-data:www-data %s' % os.path.join(env.localwiki_root))

        # Disable default apache site
        if exists('/etc/apache2/sites-enabled/000-default'):
           sudo('a2dissite default')

        install_ssl_certs()

        # Get SSL information
        get_ssl_info()

        # Install apache config
        upload_template('config/apache/localwiki', '/etc/apache2/sites-available/localwiki',
            context=env, use_jinja=True, use_sudo=True)
        sudo('a2ensite localwiki')

        # Restart apache
        sudo('service apache2 restart')

def setup_permissions():
    # Add the user we run commands with to the apache user group
    sudo('usermod -a -G www-data %s' % env.user)
    sudo('chmod g+s %s' % env.localwiki_root)

    # Allow apache to read all the files in the localwiki root
    sudo('chown -R www-data:www-data %s' % env.localwiki_root)
    # .. but don't let other users view env/, src/.
    # Apache needs 775 access to the localwiki.wsgi script, though.
    sudo('chmod 770 %s %s' % (env.virtualenv, env.src_root))

def setup_mapserver():
    """
    Enable map-a.localwiki.org, map-b.localwiki.org, map-c.localwiki.org as
    cached proxies to cloudmade tiles.
    """
    setup_varnish()
    upload_template('config/apache/map', '/etc/apache2/sites-available/map',
            context=env, use_jinja=True, use_sudo=True)
    sudo('a2ensite map')
    sudo('service apache2 restart')

def setup_varnish():
    put('config/varnish/default.vcl', '/etc/varnish/default.vcl', use_sudo=True)
    sudo('service varnish restart')

def add_ssh_keys():
    run('mkdir -p ~/.ssh && chmod 700 ~/.ssh')
    run('touch ~/.ssh/authorized_keys')
    run('mkdir ssh_to_add')
    put('config_secrets/ssh/*', 'ssh_to_add/')
    run('cat ~/ssh_to_add/* >> ~/.ssh/authorized_keys')
    run('rm -rf ~/ssh_to_add')

def attach_ebs_volumes():
    """
    Attach EBS volumes.
    """
    print "Attaching EBS volume inside of instance.."
    sudo('mkfs -t ext3 /dev/xvdh')
    sudo('mkdir -p /srv/')
    sudo('echo "/dev/xvdh       /srv    auto    defaults,nobootwait 0       2 " >> /etc/fstab')
    sudo('mount -a')

def create_ec2(ami_id=None, instance_type='m1.medium'):
    ec2()

    if not ami_id:
        ami_id = get_ec2_ami(env.ec2_region)

    conn = boto.ec2.connect_to_region(env.ec2_region,
        aws_access_key_id=env.aws_access_key_id,
        aws_secret_access_key=env.aws_secret_access_key
    )
    # Don't delete root EBS volume on termination
    root_device = boto.ec2.blockdevicemapping.BlockDeviceType(
        delete_on_termination=False,
    )
    block_device_map = boto.ec2.blockdevicemapping.BlockDeviceMapping()
    block_device_map['/dev/sda1'] = root_device
    res = conn.run_instances(ami_id,
        key_name=env.ec2_key_name,
        instance_type=instance_type,
        block_device_map=block_device_map,
        security_groups=[env.ec2_security_group]
    )

    instance = res.instances[0]
    exact_region = instance.placement

    # Create EBS volume for data storage
    print "Waiting for EBS volume to be created.."
    data_vol = conn.create_volume(300, exact_region)
    cur_vol = conn.get_all_volumes([data_vol.id])[0]
    while cur_vol.status != 'available':
        time.sleep(1)
        print ".",
        sys.stdout.flush()
        cur_vol = conn.get_all_volumes([data_vol.id])[0]

    print "Spinning up instance. Waiting for it to start. "
    while instance.state != 'running':
        time.sleep(1)
        instance.update()
        print ".",
        sys.stdout.flush()
    print "Instance running."
    print "Hostname: %s" % instance.public_dns_name

    print "Attaching EBS volume to instance at AWS level.."
    conn.attach_volume (data_vol.id, instance.id, "/dev/sdh")

    print "Waiting for instance to finish booting up. "
    time.sleep(20)
    print "Instance ready to receive connections. "
    env.hosts = [instance.public_dns_name]

def create_swap():
    put('config/init/create_swap.conf', '/etc/init/create_swap.conf', use_sudo=True)
    sudo('start create_swap')

def setup_ec2():
    """
    Things we need to do to set up the EC2 instance /after/
    we've created the instance and have its hostname.
    """
    attach_ebs_volumes()
    create_swap()

def setup_celery():
    put('config/init/celery.conf', '/etc/init/celery.conf', use_sudo=True)
    sudo('touch /var/log/celery.log')
    sudo('chown www-data:www-data /var/log/celery.log')
    sudo('chmod 660 /var/log/celery.log')
    sudo('service celery start')

def setup_mailserver():
    upload_template('config/postfix/main.cf', '/etc/postfix/main.cf',
        context=get_context(env), use_jinja=True, use_sudo=True)
    upload_template('config/postfix/master.cf', '/etc/postfix/master.cf',
        context=get_context(env), use_jinja=True, use_sudo=True)
    upload_template('config/postfix/mailname', '/etc/mailname',
        context=get_context(env), use_jinja=True, use_sudo=True)
    sudo('service postfix restart')

def provision(test_server=False):
    if env.host_type == 'vagrant':
        fix_locale()

    if env.host_type == 'ec2':
        setup_ec2()

    add_ssh_keys()
    install_system_requirements()
    setup_mailserver()
    setup_postgres(test_server=test_server)
    setup_jetty()
    setup_repo()
    init_localwiki_install()
    setup_permissions() 
    setup_celery()
    setup_apache()

    setup_mapserver()
    save_config_secrets()

def run_tests():
    # Must be superuser to run tests b/c of PostGIS requirement? Ugh..
    # XXX TODO: Fix this, somehow.  django-nose + pre-created test db?
    sudo("""psql -d postgres -c "ALTER ROLE localwiki SUPERUSER" """, user='postgres')
    with virtualenv():
        sudo('localwiki-manage test regions pages maps tags versioning diff ckeditor redirects users', user='www-data')
    sudo("""psql -d postgres -c "ALTER ROLE localwiki NOSUPERUSER" """, user='postgres')

def branch(name):
    env.branch = name

def update_code():
    with cd(env.src_root):
        sudo("git fetch origin", user="www-data")
        stash_str = sudo("git stash", user="www-data")
        sudo("git reset --hard origin/%s" % env.branch, user="www-data")
        print 'stash_str', stash_str
        if stash_str.strip() != 'No local changes to save':
            sudo("git stash pop", user="www-data")

def rebuild_virtualenv():
    with cd(env.localwiki_root):
        sudo("virtualenv --system-site-packages env", user="www-data")

def touch_wsgi():
    # Touching the deploy.wsgi file will cause apache's mod_wsgi to
    # reload all python modules having to restart apache.  This is b/c
    # we are running django.wsgi in daemon mode.
    with cd(env.localwiki_root):
        sudo("touch localwiki.wsgi")

def update(local=False):
    print 'LOCAL', local
    if not local:
        update_code()
    rebuild_virtualenv()  # rebuild since it may be out of date and broken
    with cd(env.src_root):
        with virtualenv():
            sudo("python setup.py clean --all", user="www-data")
            sudo("rm -rf dist localwiki.egg-info", user="www-data")
            update_django_settings()
            sudo("python setup.py develop", user="www-data")
            #sudo("python setup.py install")
            sudo("localwiki-manage setup_all", user="www-data")

def deploy(local=False):
    """
    Update the code (git pull) and restart / rebuild all needed services.

    Args:
        local: If True, don't update the repository on the server, but
            otherwise deploy everything else.  This is useful if you're
            doing local development via vagrant, where you don't want to
            pull down from git -- and instead want to run using your
            local changes.
    """
    update(local=local)
    setup_jetty()
    touch_wsgi()
    sudo("service memcached restart", pty=False)

def fix_locale():
    sudo('update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8')
    disconnect_all()
