Settings
========

Administration interface
------------------------

LocalWiki comes with a web-based admin interface.  If LocalWiki is running on
your machine, it can be found at http://localhost/admin/

.. figure:: /_static/images/admin_login.png

At the prompt, enter your superuser login and password.

When you login, you will see all of the object types that you can modify on the
left, and a list of recent actions done by administrators on the right(if any).

.. figure:: /_static/images/admin_home.png



Domain name and site name
-------------------------

In the admin interface, go to "Sites", click on the site you want to modify,
enter the domain name and display name and press "Save".

.. figure:: /_static/images/admin_site.png


``localsettings.py``
--------------------

Settings particular to your installation go in this file, found at 
``/usr/share/localwiki/conf/localsettings.py`` on your system. Here are some
things you may need or wish to modify:

``SITE_THEME``
    The name of the directory under ``themes`` to look for the theme templates
    and static files.

``OLWIDGET_DEFAULT_OPTIONS``
    Defaults for all map widgets, including default location, theme, navigation
    controls, colors, etc.  To set the default map location, change
    ``default_lat`` and ``default_lon``.  Use this tool to look it up:
    http://www.getlatlon.com/

``CLOUDMADE_API_KEY``
    Your developer API key from `Cloudmade <http://developers.cloudmade.com/>`_

``EMBED_ALLOWED_URLS``
    This is a list of regular expressions used to restrict what kinds of
    content users can embed.  If an embedded URL does not pass any of the
    regular expressions in this list, it will not be shown.
