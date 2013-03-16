# http://stackoverflow.com/questions/59895/can-a-bash-script-tell-what-directory-its-in
HERE=`(cd "${0%/*}" 2>/dev/null; echo "$PWD"/)`

if [[ "$OSTYPE" == "darwin"* ]]; then
    # Set a symbolic link so it's possible to use a non-version-specific plist
    ln -s /usr/local/Cellar/jetty/8.* /usr/local/Cellar/jetty/jetty 
    ln -s /usr/local/Cellar/solr14/1.* /usr/local/Cellar/solr14/solr

    # Move over diff app
    cp $HERE/daisydiff.war /usr/local/Cellar/jetty/jetty/libexec/webapps/

    # Backup solr config
    mv /usr/local/Cellar/solr14/solr/libexec/example/solr/conf/schema.xml /usr/local/Cellar/solr14/solr/libexec/example/solr/conf/schema.xml.orig
    # Copy over solr config
    cp $HERE/solr_schema.xml /usr/local/Cellar/solr14/solr/libexec/example/solr/conf/schema.xml

    # Set up solr as a jetty webapp
    ln -s /usr/local/Cellar/solr14/solr/libexec/example/webapps/solr.war /usr/local/Cellar/jetty/jetty/libexec/webapps/

    # Make jetty start automatically.
    cp $HERE/os_x/org.jetty.jetty.plist ~/Library/LaunchAgents/
    launchctl load ~/Library/LaunchAgents/org.jetty.jetty.plist
else
    sudo sed -i 's/NO_START=1/NO_START=0/g' /etc/default/jetty
    sudo cp /etc/solr/conf/schema.xml /etc/solr/conf/schema.xml.orig
    sudo cp $HERE/solr_schema.xml /etc/solr/conf/schema.xml
    sudo cp $HERE/daisydiff.war /var/lib/jetty/webapps
    sudo service jetty stop
    sudo service jetty start
fi
