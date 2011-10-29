python fix_packages.py ../
cd ..
rm -r deb_dist/
rm -r localwiki.egg-info/
python setup.py --command-packages=stdeb.command sdist_dsc --ignore-install-requires
cd deb_utils
cp python-localwiki.postinst ../deb_dist/localwiki-0.1.pre-alpha/debian
cd ../deb_dist/localwiki-0.1.pre-alpha
dpkg-buildpackage -rfakeroot -S -sa
cd ../
dput ppa:mivanov/localwiki localwiki_0.1.pre-alpha-1_source.changes
cd ../deb_utils

