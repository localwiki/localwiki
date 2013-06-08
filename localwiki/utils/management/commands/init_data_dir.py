import sys
import os
import shutil
import errno


class Command(object):
    def handle(self, *args, **kwargs):
        """
        Initializes the installation-specific data directory which
        contains things like user uploads and installation-specific
        settings.
        """
        share_dir = os.path.join(sys.prefix, 'share')
        data_dir = os.path.join(share_dir, 'localwiki')

        # Create the data directory and copy defaults into it.
        if not os.path.exists(share_dir):
            os.makedirs(share_dir)

        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        defaults_dir = os.path.join(self.PROJECT_ROOT, 'etc', 'install_config',
            'defaults')

        for item in os.listdir(os.path.join(defaults_dir, 'localwiki')):
            if os.path.exists(os.path.join(data_dir, item)):
                sys.stderr.write("Directory %s already exists! Skipping..\n" %
                    os.path.join(data_dir, item))
                continue
            src = os.path.join(defaults_dir, 'localwiki', item)
            dst = os.path.join(data_dir, item)
            try:
                shutil.copytree(src, dst)
            except OSError as exc:
                if exc.errno == errno.ENOTDIR:
                    shutil.copy(src, dst)
                else:
                    raise

        # Rename localsettings.py.template to localsettings.py
        os.rename(os.path.join(data_dir, 'conf', 'localsettings.py.template'),
                  os.path.join(data_dir, 'conf', 'localsettings.py'))

        print ('Created data directory in %s\n' % data_dir)


def run(DATA_ROOT=None, PROJECT_ROOT=None):
    c = Command()
    c.DATA_ROOT = DATA_ROOT
    c.PROJECT_ROOT = PROJECT_ROOT
    c.handle()
