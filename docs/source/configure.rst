Web server configuration
========================

While you can run the LocalWiki software using the built-in development server,
for a public-facing setup you're definitely better off using it with Apache and
mod_wsgi.

Here is a sample Apache configuration file::

  <VirtualHost *:80>
    ServerAdmin webmaster@example.org
    ServerName example.org
    ServerAlias example.org www.example.org

    DocumentRoot /srv/sites/example/sapling

    <Directory /srv/sites/example/>
        Options -Indexes FollowSymLinks MultiViews
        AllowOverride None
        Order allow,deny
        allow from all
    </Directory>

    # gzip content for much faster page loads.
    <Location />
        # Insert filter
        SetOutputFilter DEFLATE

        # Netscape 4.x has some problems...
        BrowserMatch ^Mozilla/4 gzip-only-text/html
        # Netscape 4.06-4.08 have some more problems
        BrowserMatch ^Mozilla/4\.0[678] no-gzip
        # MSIE masquerades as Netscape, but it is fine
        # BrowserMatch \bMSIE !no-gzip !gzip-only-text/html
        # NOTE: Due to a bug in mod_setenvif up to Apache 2.0.48
        # the above regex won't work. You can use the following
        # workaround to get the desired effect:
        BrowserMatch \bMSI[E] !no-gzip !gzip-only-text/html
    
        # Don't compress images
        SetEnvIfNoCase Request_URI \
        \.(?:gif|jpe?g|png)$ no-gzip dont-vary
              
        # Make sure proxies don't deliver the wrong content
        Header append Vary User-Agent env=!dont-vary
    </Location>

    # Dont' gzip the user-uploaded content in the media directory.
    # The content is assumed to be JPEG, PNG, etc, which is already
    # compressed.
    <Location /media/>
        SetEnv no-gzip
    </Location>

    ErrorLog /var/log/apache2/error.log

    # Possible values include: debug, info, notice, warn, error, crit,
    # alert, emerg.
    LogLevel warn

    CustomLog /var/log/apache2/access.log combined

    WSGIScriptAlias / /srv/sites/example/sapling/deploy/django.wsgi

    Alias /robots.txt /srv/sites/example/sapling/static/robots.txt
    Alias /favicon.ico /srv/sites/example/sapling/static/favicon.ico
    Alias /media/ /srv/sites/example/sapling/media/
    Alias /static/ /srv/sites/example/sapling/static/

    # The media directory, which contains user-uploaded content,
    # should be set to force downloads. This is *extremely* important
    # for security reasons.
    <Location /media/>
        Header set Content-Disposition attachment
    </Location>

  </VirtualHost>
