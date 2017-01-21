# http://stackoverflow.com/questions/59895/can-a-bash-script-tell-what-directory-its-in
HERE=`(cd "${0%/*}" 2>/dev/null; echo "$PWD"/)`

sed -i 's/NO_START=1/NO_START=0/g' /etc/default/jetty
cp /etc/solr/conf/schema.xml /etc/solr/conf/schema.xml.orig
cp $HERE/solr_schema.xml /etc/solr/conf/schema.xml
cp $HERE/daisydiff.war /var/lib/jetty/webapps
service jetty stop
service jetty start
