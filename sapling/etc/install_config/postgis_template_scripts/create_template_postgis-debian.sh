#!/bin/bash

# For Ubuntu 8.x and 9.x releases.
if [ -d "/usr/share/postgresql-8.3-postgis" ]
then
    POSTGIS_SQL_PATH=/usr/share/postgresql-8.3-postgis
    POSTGIS_SQL=lwpostgis.sql
fi

# For Ubuntu 10.04
if [ -d "/usr/share/postgresql/8.4/contrib" ]
then
    POSTGIS_SQL_PATH=/usr/share/postgresql/8.4/contrib
    POSTGIS_SQL=postgis.sql
fi

# For Ubuntu 10.10 and Ubuntu 11.04 (with PostGIS 1.5)
if [ -d "/usr/share/postgresql/8.4/contrib/postgis-1.5" ]
then
    POSTGIS_SQL_PATH=/usr/share/postgresql/8.4/contrib/postgis-1.5
    POSTGIS_SQL=postgis.sql
    GEOGRAPHY=1
fi

# For Ubuntu 11.10 (with PostGIS 1.5)
if [ -d "/usr/share/postgresql/9.1/contrib/postgis-1.5" ]
then
    POSTGIS_SQL_PATH=/usr/share/postgresql/9.1/contrib/postgis-1.5
    POSTGIS_SQL=postgis.sql
    GEOGRAPHY=1
else
    GEOGRAPHY=0
fi

createdb template_postgis -E UTF8 -T template0
OUT=$?
# template doesn't exist yet, so let's create
if [ $OUT -eq 0 ]
then
   createlang -d template_postgis plpgsql
   psql -d postgres -c "UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis';"
   psql -d template_postgis -f $POSTGIS_SQL_PATH/$POSTGIS_SQL
   psql -d template_postgis -f $POSTGIS_SQL_PATH/spatial_ref_sys.sql
   psql -d template_postgis -c "GRANT ALL ON geometry_columns TO PUBLIC;"
   psql -d template_postgis -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"

   if ((GEOGRAPHY))
   then
       psql -d template_postgis -c "GRANT ALL ON geography_columns TO PUBLIC;"
   fi

else
   exit
fi
