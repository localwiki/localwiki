#!/bin/bash

POSTGIS_SQL_PATH=/usr/local/share/postgis/
POSTGIS_SQL=postgis.sql
GEOGRAPHY=1

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
