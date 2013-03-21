Settings
========

Administration interface
------------------------

LocalWiki comes with a web-based admin interface.  If LocalWiki is running on
your machine, it can be found at ``http://localhost/admin/``.  Otherwise,
you can find the admin interface at ``http://<your server's address>/admin/``

.. figure:: /_static/images/admin_login.png

At the prompt, enter your superuser login and password.  If you don't
have a superuser login and password, you can create one by running
``sudo localwiki-manage createsuperuser``.

When you login, you will see all of the object types that you can modify on the
left, and a list of recent actions done by administrators on the right(if any).

.. figure:: /_static/images/admin_home.png



Domain name and site name
-------------------------

In the admin interface, go to "Sites", click on the site you want to modify,
enter the domain name and display name and press "Save".

.. figure:: /_static/images/admin_site.png


Setting the default map location
--------------------------------

You'll need to edit your ``localsettings.py`` file and set the default
map location.  See the ``localsettings.py`` section below.


``localsettings.py``
--------------------

Settings particular to your installation go in this file, found at 
``/usr/share/localwiki/conf/localsettings.py`` on your system. Here are some
things you may need or wish to modify:

``OLWIDGET_DEFAULT_OPTIONS``
    Defaults for all map widgets, including default location, theme, navigation
    controls, colors, etc.
    
    You will want to set the the **default map location** on your localwiki.
    Simply change ``default_lat`` and ``default_lon``.  Use this tool to look it
    up: http://www.getlatlon.com/

``CLOUDMADE_API_KEY``
    Your developer API key from `Cloudmade <http://developers.cloudmade.com/>`_

``GOOGLE_ANALYTICS_ID``
    Your ID from `Google Analytics <http://www.google.com/analytics/>`_

``SITE_THEME``
    The name of the directory under ``themes`` to look for the theme templates
    and static files.  We'll have more detail on creating a theme soon.

``EMBED_ALLOWED_URLS``
    This is a list of regular expressions used to restrict what kinds of
    content users can embed.  If an embedded URL does not pass any of the
    regular expressions in this list, it will not be shown.

``LANGUAGE_CODE``
    LocalWiki is fully localized and is currently translated into a
    number of languages.  To change your instance's language, set this
    to one of: ``en-us`` (for English), ``ja`` (Japanese),
    ``it_IT`` (Italian), ``pt_PT`` (Portuguese), ``ru_RU`` (Russian),
    ``de_CH`` (German, CH), ``es_AR`` (Spanish, Argentina), ``da_DK`` (Danish).

After changing settings you'll need to restart Apache.  On most systems
you can do this by running ``sudo /etc/init.d/apache2 restart``.
