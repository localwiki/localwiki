#!/bin/bash
# Makes deb source for a given Ubuntu release using prebuilt source
# and uploads it to the localwiki PPA

if [[ "$1" = "" ]] || [[ "$2" = "" ]]
then
  echo "Usage: $0 <ubuntu_release(ex: lucid)> <prebuilt_dist.orig.tar.gz>"
  exit
fi

cd ..
LW_VERSION=$(python -c "from sapling import get_version; print get_version().replace(' ', '.')")
UBUNTU_RELEASE=$1
DEBIAN_VERSION="0ubuntu1~${UBUNTU_RELEASE}"
DIST_FILE=$2
VERSION="${LW_VERSION}-${DEBIAN_VERSION}"
echo "Building package source for localwiki_${VERSION}"

rm -r deb_dist/
rm -r localwiki.egg-info/

python setup.py --command-packages=stdeb.command sdist_dsc --ignore-install-requires --suite ${UBUNTU_RELEASE} --debian-version ${DEBIAN_VERSION}  --use-premade-distfile ${DIST_FILE}

cp deb_utils/localwiki.postinst deb_dist/localwiki-${LW_VERSION}/debian
cp deb_utils/triggers deb_dist/localwiki-${LW_VERSION}/debian
cd deb_dist/localwiki-${LW_VERSION}

dpkg-buildpackage -rfakeroot -S -sd

cd ../
dput ppa:localwiki/ppa localwiki_${VERSION}_source.changes
cd ../deb_utils
