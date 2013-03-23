#!/bin/bash
UBUNTU_RELEASES="lucid natty oneiric precise quantal"

if [[ "$1" = "" ]]
then
  echo "Usage: $0 <user/ppa>"
  echo "Official LocalWiki PPA is localwiki/ppa"
  echo "For testing use localwikidev/testing"
  exit
fi

PPA=$1

# Build orig.tar.gz
cd ..
rm -r deb_dist/
rm -r localwiki.egg-info/
python setup.py --command-packages=stdeb.command sdist_dsc --ignore-install-requires
cd deb_dist/
ORIG_FILE=$(ls *.orig.tar.gz)
mv ${ORIG_FILE} /tmp

cd ../deb_utils
for DIST in $(echo ${UBUNTU_RELEASES}) ; do
    echo "Building and uploading for ${DIST} ..."
    ./makedeb_ppa.sh "${DIST}" "/tmp/${ORIG_FILE}" "${PPA}"
done
