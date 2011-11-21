#!/bin/bash
UBUNTU_RELEASES="lucid maverick natty oneiric"

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
    ./makedeb_ppa.sh "${DIST}" "/tmp/${ORIG_FILE}"
done
