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
sample:

.. literalinclude:: ../../install_config/apache.conf.template

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
