Web server configuration
========================


Normal installation
--------------------

If you installed the LocalWiki software using the Ubuntu package then an
Apache site should be automatically up and running.  Its configuration file
can found in ``/etc/apache2/sites-enabled/example.com``.  You'll want to
open that file and change the server name, etc.

Please see the `official Apache documentation <http://httpd.apache.org/docs/>`_
for all possible configuration values.


Development server
------------------

If you're doing development or testing, you can run ``localwiki-manage runserver``
to start the built-in webserver.  Don't use this in production.


Manual installations
--------------------

If you installed LocalWiki manually then you'll need to copy the
wsgi template file and edit it::

  mkdir deploy
  cp install_config/localwiki_virtualenv.wsgi.template deploy/localwiki.wsgi

Then open up ``localwiki.wsgi`` and set ``VIRTUAL_ENV_PATH`` to the absolute
path to the virtualenv you installed LocalWiki in.

Then you'll need to create an Apache configuration file.  Here's a
sample::

  <VirtualHost *:80>
    ServerAdmin webmaster@example.org
    ServerName example.org
    ServerAlias example.org www.example.org

    CustomLog /var/log/apache2/access.log combined

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

    WSGIDaemonProcess localwiki threads=15 maximum-requests=10000
    WSGIScriptAlias / /path/to/your/deploy/localwiki.wsgi
    WSGIProcessGroup localwiki

    Alias /robots.txt /path/to/your/env/share/localwiki/static/robots.txt
    Alias /favicon.ico /path/to/your/env/share/localwiki/static/favicon.ico
    Alias /media/ /path/to/your/env/share/localwiki/media/
    Alias /static/ /path/to/your/env/share/localwiki/static/

    # The media directory, which contains user-uploaded content,
    # should be set to force downloads. This is *extremely* important
    # for security reasons.
    <Location /media/>
            Header set Content-Disposition attachment
    </Location>

You'll need to set some of these values:

``ServerAdmin``, ``ServerName``, and ``ServerAlias`` should be
self-explanatory.  Read the Apache docs for more info.

``WSGIScriptAlias / /path/to/your/deploy/localwiki.wsgi`` -- you'll need to
change ``/path/to/your/deploy/`` to be the path to where the ``localwiki.wsgi``
file lives.

In all of the ``Alias ...`` lines you'll need to change
``/path/to/your/env`` to be the absolute path to the virtualenv where
you installed LocalWiki.

After you make you're changes you'll need to restart Apache.
Please see the `official Apache documentation <http://httpd.apache.org/docs/>`_
for more on all this.
