#!/bin/bash
# Prints out the package dependencies for a specific Ubuntu release

if [ $# -eq 0 ]
then
  echo "Usage: $0 <ubuntu_release(ex: lucid)>"
  exit 1
fi

depends="python-pip, python-virtualenv, python-setuptools, solr-jetty, python-lxml, python-imaging, gdal-bin, python-psycopg2, libapache2-mod-wsgi, git-core, mercurial, subversion"

if [ "$1" = "oneiric" -o "$1" = "precise" -o "$1" = "quantal" ]
then
  depends="${depends}, postgresql-9.1-postgis"
else
  depends="${depends}, postgresql-8.4-postgis"
fi

# Starting with quantal (12.10), the metapackage 'proj' was deprecated.
if [ "$1" = "quantal" ]
then
  depends="${depends}, proj-bin"
else
  depends="${depends}, proj"
fi

if [ "$1" = "precise" ]
then
  depends="default-jre-headless, ${depends}"
fi

echo ${depends}
