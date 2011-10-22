import sys
import os
import shutil


class Command(object):
    def handle(self, *args, **kwargs):
        """
        Initializes the installation-specific data directory which
        contains things like user uploads and installation-specific
        settings.
        """
        share_dir = os.path.join(sys.prefix, 'share')
        data_dir = os.path.join(share_dir, 'localwiki')

        # Check to make sure the data directory doesn't already exist.
        if os.path.exists(data_dir):
            sys.stderr.write("Data directory %s already exists!\n" % data_dir)
            return

        # Create the data directory and copy defaults into it.
        if not os.path.exists(share_dir):
            os.makedirs(share_dir)
        defaults_dir = os.path.join(self.PROJECT_ROOT, 'install_config',
            'defaults')
        shutil.copytree(os.path.join(defaults_dir, 'localwiki'), data_dir)

        print ('Created data directory in %s\n' % data_dir)

def run(DATA_ROOT=None, PROJECT_ROOT=None):
    c = Command()
    c.DATA_ROOT = DATA_ROOT
    c.PROJECT_ROOT = PROJECT_ROOT
    c.handle()
