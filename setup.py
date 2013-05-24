from setuptools import setup, find_packages
import os
import sys
from fnmatch import fnmatchcase
from distutils.util import convert_path

from sapling import get_version


# Provided as an attribute, so you can append to these instead
# of replicating them:
standard_exclude = ('*.py', '*.pyc', '*$py.class', '*~', '.*', '*.bak')
standard_exclude_directories = ('.*', 'CVS', '_darcs', './build',
                                './dist', 'EGG-INFO', '*.egg-info')

# (c) 2005 Ian Bicking and contributors; written for Paste (http://pythonpaste.org)
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Note: you may want to copy this into your setup.py file verbatim, as
# you can't import this from another package, when you don't know if
# that package is installed yet.
def find_package_data(
    where='.', package='',
    exclude=standard_exclude,
    exclude_directories=standard_exclude_directories,
    only_in_packages=True,
    show_ignored=False):
    """
    Return a dictionary suitable for use in ``package_data``
    in a distutils ``setup.py`` file.

    The dictionary looks like::

        {'package': [files]}

    Where ``files`` is a list of all the files in that package that
    don't match anything in ``exclude``.

    If ``only_in_packages`` is true, then top-level directories that
    are not packages won't be included (but directories under packages
    will).

    Directories matching any pattern in ``exclude_directories`` will
    be ignored; by default directories with leading ``.``, ``CVS``,
    and ``_darcs`` will be ignored.

    If ``show_ignored`` is true, then all the files that aren't
    included in package data are shown on stderr (for debugging
    purposes).

    Note patterns use wildcards, or can be exact paths (including
    leading ``./``), and all searching is case-insensitive.
    """
    out = {}
    stack = [(convert_path(where), '', package, only_in_packages)]
    while stack:
        where, prefix, package, only_in_packages = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if os.path.isdir(fn):
                bad_name = False
                for pattern in exclude_directories:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        if show_ignored:
                            print >> sys.stderr, (
                                "Directory %s ignored by pattern %s"
                                % (fn, pattern))
                        break
                if bad_name:
                    continue
                if (os.path.isfile(os.path.join(fn, '__init__.py'))
                    and not prefix):
                    if not package:
                        new_package = name
                    else:
                        new_package = package + '.' + name
                    stack.append((fn, '', new_package, False))
                else:
                    stack.append((fn, prefix + name + '/', package, only_in_packages))
            elif package or not only_in_packages:
                # is a file
                bad_name = False
                for pattern in exclude:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        if show_ignored:
                            print >> sys.stderr, (
                                "File %s ignored by pattern %s"
                                % (fn, pattern))
                        break
                if bad_name:
                    continue
                out.setdefault(package, []).append(prefix + name)
    return out


def gen_data_files(*dirs):
    results = []
    for dir_info in dirs:
        if type(dir_info) == tuple:
            src_dir, name = dir_info
        else:
            name = dir_info
            src_dir = dir_info
        top_root = None
        for root, dirs, files in os.walk(src_dir):
            if top_root is None:
                top_root = root
            root_name = root.replace(top_root, name, 1)
            results.append((root_name, map(lambda f: root + "/" + f, files)))
    return results


install_requires = [
    'setuptools',
    'django==1.3',
    'html5lib==0.95',
    'sorl-thumbnail==11.12',
    'python-dateutil==1.5',
    'pysolr==2.1.0-beta',
    'django-haystack==1.2.6',
    'django-randomfilenamestorage==1.1',
    'django-guardian==1.0.4',
    'South==0.7.4',
    'python-flot-utils==0.2.1',
    'django-staticfiles==1.2.1',
    'django-registration==0.8.0',
    'django-olwidget==0.46-custom1',
    'django-honeypot==0.3.0-custom4',
    'django-tastypie==0.9.12-custom5',
    'django-qsstats-magic==0.7',
    'django-picklefield==0.3.0',
    'django-constance==0.6.0',
]
if int(os.getenv('DISABLE_INSTALL_REQUIRES', '0')):
    install_requires = None

setup(
    name='localwiki',
    version=get_version(),
    description="LocalWiki is a tool for collaboration in local communities",
    long_description=open(os.path.join('install_config','DESCRIPTION_pypi.txt')).read(),
    author='Mike Ivanov',
    author_email='mivanov@gmail.com',
    url='http://localwiki.org',
    packages=find_packages(),
    package_dir={'sapling': 'sapling'},
    data_files=gen_data_files(
        ('docs', 'share/localwiki/docs'),
    ),
    package_data=find_package_data(exclude_directories=standard_exclude_directories + ('deb_utils',) ),
    install_requires=install_requires,
    dependency_links=[
        'https://github.com/philipn/olwidget/tarball/custom_base_layers_fixed#egg=django-olwidget-0.46-custom1',
        'https://github.com/philipn/django-honeypot/tarball/b4991c140849901d2f8842df2c4672813e73381b#egg=django-honeypot-0.3.0-custom4',
        'https://github.com/philipn/django-tastypie/tarball/localwiki_master#egg=django-tastypie-0.9.12-custom5',
    ],
    entry_points={
        'console_scripts': ['localwiki-manage=sapling.manage:main'],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet',
        'Topic :: Communications :: Conferencing',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Office/Business :: Groupware',
    ],
)
