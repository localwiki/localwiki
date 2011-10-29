python fix_packages.py ../
cd ..
rm -r deb_dist/
rm -r localwiki.egg-info/
python setup.py --command-packages=stdeb.command sdist_dsc --ignore-install-requires
cd deb_utils
cp python-localwiki.postinst ../deb_dist/localwiki-0.1.pre-alpha/debian
cd ../deb_dist/localwiki-0.1.pre-alpha
dpkg-buildpackage -rfakeroot -uc -us
cd ../../deb_utils
