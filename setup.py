from setuptools import setup, find_packages
import os
import sys
from fnmatch import fnmatchcase
from distutils.util import convert_path

from localwiki import get_version

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


def find_packages_in(dirs):
    """
    Given a list of directories, `dirs`, we use `find_packages()` on each and
    return the result as a list of qualified packages, e.g.

    find_packages_in(['localwiki']) -> ['localwiki', 'localwiki.pages', ...]
    """
    packages = []
    for dir in dirs:
        packages.append(dir)
        packages += [ '%s.%s' % (dir, p) for p in find_packages(dir) ]
    return packages


install_requires = [
    'setuptools',
    'django==1.5.4',
    'html5lib==0.95',
    'requests==2.0.0',
    'python-memcached==1.53',
    'sorl-thumbnail==11.12-custom5',
    'python-dateutil==1.5',
    'pysolr==2.1.0-beta',
    'django-haystack==2.1.0',
    'django-randomfilenamestorage==1.1',
    'django-guardian==1.1.1',
    'South==0.8.1-custom2',
    'python-flot-utils==0.2.1',
    'django-staticfiles==1.2.1',
    'django-registration==0.8.0',
    'django-olwidget==0.46-custom2',
    'django-honeypot==0.4.0-custom2',
    'django-qsstats-magic==0.7',
    'django-picklefield==0.3.0',
    'django-constance==0.6-custom1',
    'celery[redis]==3.1.3',
    'celery-haystack==0.7.2',
    'django-extensions==1.2.5',
    'djangorestframework==2.3.13-custom1',
    'django-filter==0.7',
    'djangorestframework-filter==0.2.1',
    'djangorestframework-gis==0.1.0-custom2',
    'markdown==2.3.1',
    'django-cors-headers==0.12',
    'django-gravatar2==1.1.3',
    'django-endless-pagination==2.0',
    'django-follow==0.6.1',
    'django-templated-email==0.4.9',
    'django-block-ip==0.1.6',
    'django-static-sitemaps==2.1.0-custom1',
    'django-celery-email==1.0.4-custom1',
    'django-activity-stream==0.4.5beta1',
    'django-jsonfield==0.9.12',
    'psycopg2==2.5.3',
]
if int(os.getenv('DISABLE_INSTALL_REQUIRES', '0')):
    install_requires = None

setup(
    name='localwiki',
    version=get_version(),
    description="LocalWiki is a tool for collaboration in local communities",
    long_description=open(os.path.join('config','DESCRIPTION_pypi.txt')).read(),
    author='Mike Ivanov',
    author_email='mivanov@gmail.com',
    url='http://localwiki.org',
    packages=find_packages_in(['localwiki']),
    package_dir={'localwiki': 'localwiki'},
    data_files=gen_data_files(
        ('docs', 'share/localwiki/docs'),
    ),
    package_data=find_package_data(exclude_directories=standard_exclude_directories + ('deb_utils',) ),
    install_requires=install_requires,
    dependency_links=[
        'https://github.com/philipn/olwidget/tarball/5c8eb75aaf0739b35fa06b0ba75f30bd32b89e77#egg=django-olwidget-0.46-custom2',
        'https://github.com/philipn/django-honeypot/tarball/localwiki#egg=django-honeypot-0.4.0-custom2',
        'https://github.com/philipn/sorl-thumbnail/tarball/localwiki#egg=sorl-thumbnail-11.12-custom5',
        'https://github.com/philipn/django-south/tarball/localwiki_master#egg=South-0.8.1-custom2',
        'https://github.com/philipn/django-constance/tarball/localwiki#egg=django-constance-0.6-custom1',
        'https://github.com/philipn/django-rest-framework/tarball/localwiki#egg=djangorestframework-2.3.13-custom1',
        'https://github.com/philipn/django-rest-framework-chain/tarball/django_rest_framework_filter#egg=djangorestframework-filter-0.2.1',
        'https://github.com/philipn/django-rest-framework-gis/tarball/localwiki#egg=djangorestframework-gis-0.1.0-custom2',
        'https://github.com/philipn/django-endless-pagination/tarball/zip_safe#egg=django-endless-pagination-2.0',
        'https://github.com/philipn/django-static-sitemaps/tarball/localwiki#egg=django-static-sitemaps-2.1.0-custom1',
        'https://github.com/philipn/django-celery-email/tarball/localwiki#egg=django-celery-email-1.0.4-custom1',
    ],
    entry_points={
        'console_scripts': ['localwiki-manage=localwiki.manage:main'],
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
