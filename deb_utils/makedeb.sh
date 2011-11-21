#!/bin/bash
# Used for local testing only!
# Builds a binary .deb with suite set to "unstable"

cd ..
LW_VERSION=$(python -c "from sapling import get_version; print get_version().replace(' ', '.')")

rm -r deb_dist/
rm -r localwiki.egg-info/

python setup.py --command-packages=stdeb.command sdist_dsc --ignore-install-requires --suite unstable

cp deb_utils/localwiki.postinst deb_dist/localwiki-${LW_VERSION}/debian
cp deb_utils/triggers deb_dist/localwiki-${LW_VERSION}/debian
cd deb_dist/localwiki-${LW_VERSION}

dpkg-buildpackage -rfakeroot -uc -us
cd ../../deb_utils
