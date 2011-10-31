cd ..
version=$(python -c "from sapling import get_version; print get_version().replace(' ', '.')")
rm -r deb_dist/
rm -r localwiki.egg-info/
python setup.py --command-packages=stdeb.command sdist_dsc --ignore-install-requires
cd deb_utils
cp python-localwiki.postinst ../deb_dist/localwiki-$version/debian
cp triggers ../deb_dist/localwiki-$version/debian
cd ../deb_dist/localwiki-$version
dpkg-buildpackage -rfakeroot -uc -us
cd ../../deb_utils
