cd ..
version=$(python -c "from sapling import get_version; print get_version().replace(' ', '.')")
rm -r deb_dist/
rm -r localwiki.egg-info/
python setup.py --command-packages=stdeb.command sdist_dsc --ignore-install-requires
cd deb_utils
cp localwiki.postinst ../deb_dist/localwiki-$version/debian
cp triggers ../deb_dist/localwiki-$version/debian
cd ../deb_dist/localwiki-$version
dpkg-buildpackage -rfakeroot -S -sa
cd ../
dput ppa:localwiki/ppa localwiki_$version-1_source.changes
cd ../deb_utils

