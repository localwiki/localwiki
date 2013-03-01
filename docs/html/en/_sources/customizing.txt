Customizing your localwiki's appearance
=======================================

It's possible to completely customize the appearance and some of the
behavior of the LocalWiki software without having to dig into the
underlying code.  You can do this by customizing the site's CSS, the
site's templates, and by creating entirely new themes.

We're hoping to make the process of altering templates and CSS a bit
less technical at some point.  For now you'll need to be comfortable
with moving things around on a server, editing files and have some
knowledge of CSS and HTML.

.. note:: If you're a developer and have been playing around, make sure
   you have set ``DEBUG`` to ``False`` in ``localsettings.py``,
   otherwise you won't see static media show up when using
   ``localwiki-manage runsever``.


Template files
--------------

The LocalWiki software has the concept of a *template*.  A template is
a text file on the server running the LocalWiki software, and it's used to
generate pages throughout the site.

.. note:: These *template files* are very different from "Template pages" on
   the wiki. Template pages on the wiki are for creating new pages more
   easily. *Template files* on the server are used by the LocalWiki software to
   generate the site itself.

These templates are simply
`Django templates <https://docs.djangoproject.com/en/dev/topics/templates/>`_
and support the full range of capabilities of the Django templating
language.  Check out the `Django template documentation <https://docs.djangoproject.com/en/dev/topics/templates/>`_
for everything that's possible with the templates.  You don't need to read the
template documentation to make simple customizations, though.

The global template directory is ``/usr/share/localwiki/templates``, or
``env/share/localwiki/templates`` (for manual installations).


Themes
------

A *theme* is a collection of templates and static assets that together control
the look of the entire site.

Each theme is simply a directory containing:

* A directory with templates (``templates/``)
* A directory with static assets (``assets/``) like CSS and images.


The global themes directory is ``/usr/share/localwiki/themes``, or
``env/share/localwiki/themes`` (for manual installations).  *NOTE*: If
you are running localwiki-0.2-beta-12 you may have to create this
directory by hand.


Tutorial
--------

The theme system is best explained through a few simple examples.

.. _example1:

Example 1: Adding a logo
~~~~~~~~~~~~~~~~~~~~~~~~
Let's add a logo to our site.  Because this is just a simple change,
making an new theme is overkill.

First, let's find the built-in templates.  Type::

    localwiki-manage shell

then once you're in the localwiki shell, copy and paste this::

    import sapling; print sapling.__path__[0]; exit()

This will print out where the localwiki code itself lives on your
system.

.. note:: It's not a good idea to modify the files in the code directory
   directly, as they're likely to be replaced when you upgrade.  If you
   want to customize the code you should do a :ref:`development install <dev-install>`.

Copy the path printed out and ``cd`` there.  You'll see there's a
``themes`` directory in that directory.  Inside the ``themes`` directory
is a directory for the default built-in theme, ``sapling``.

As explained earlier, the ``sapling`` theme directory has an ``assets``
and a ``templates`` directory inside of it::

    $ ls sapling
    assets  LICENSE.txt  README  templates

If we go inside the templates directory, we'll see a ``site`` directory
containing some template files::

    $ cd templates
    $ ls
    site
    $ cd site
    $ ls
    base.html  login_info.html  nav.html  search_form.html  site_title.html

Taking a look at the template files, the ``site_title.html`` file is
what we want to customize to add our own logo.  Let's copy that template
over to our global templates directory and then customize it.

First, let's make a ``site`` directory inside our global template
directory (explained above).

The global template directory is ``/usr/share/localwiki/templates``, or
``env/share/localwiki/templates`` (for manual installs)::

    mkdir /usr/share/localwiki/templates/site

then copy the file over::

    cp site_title.html /usr/share/localwiki/templates/site

Now we simply open up the copy of the template we made,
``/usr/share/localwiki/templates/site/site_title.html``.  It looks like
this::

    {% block site_title %}
    {% if current_site %}
      <h1><a href="{% url pages:frontpage %}">{{ current_site.name }}</a></h1>
    {% endif %}
    {% endblock %}

Let's change it to look like this::

    {% block site_title %}
    {% if current_site %}
      <a href="{% url pages:frontpage %}"><img src="{{ STATIC_URL }}/img/logo.png?v=1" alt="{{ current_site.name }}"/></a>
    {% endif %}
    {% endblock %}

Now we need to go design a pretty logo, name it ``logo.png`` and move it
into the static directory, located at ``/usr/share/localwiki/static`` or
``env/share/localwiki/static`` (for manual installations).

Once we've done all this we'll need to restart the webserver.  You can
usually do this by running the command::

    sudo /etc/init.d/apache2 restart

And you'll have a shiny new logo on your site!


Example 2: Adding a custom CSS file on every page
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you look at https://dentonwiki.org, you'll see they've got a cool "I want to
create a page about _______" banner on their front page:

.. figure:: /_static/images/css_table_dentonwiki.jpg

The DentonWiki achieves this by creating a table and then giving it a
custom CSS class.  If you click on "View source" on
https://dentonwiki.org, you'll see::

    <table class="welcome">
      <tbody>
        <tr>
          <td style="text-align: right;">
            <h1>
            Welcome to <a href="DentonWiki">Denton Wiki</a>!</h1>
            <h3>
            A website about Denton that <em>anyone</em> can edit</h3>
            <br />
            <br />
            <br />
            <br />
            <br />
            <br />
            <br />
            <h1>
            	I want to make a page about <input class="plugin searchbox" type="text" value="" /></h1>
          </td>
        </tr>
      </tbody>
    </table>

You can easily add a custom CSS class to a table by right-clicking on it
while editing and going to Table properties -> Advanced settings -> CSS classes.

But in order to make a custom CSS class work, we'll need to make a new
CSS file and reference it from the page's HTML.  Here's how we do this:

1. We make a new file, in our case named ``denton.css``, inside of the
global static directory.  In our case, this is
``/usr/share/localwiki/static/css/denton.css`` (or
``env/share/localwiki/static/css`` for manual installations).

2. Inside ``denton.css`` we place the following contents, which
customize the appearance of tables with the class ``welcome``::

    #page .welcome td {
        display: block;
        max-width: 1360px;
        height: 280px;
        background-image: url(/front_page/_files/welcome.jpg);
        background-position: 66% 0%;
        background-repeat: no-repeat;
        padding: 2em;
        border: 3px solid #b5b5b5;
    }
    #page .welcome {
        width: 100%;
        border: none;
    }
    #page .welcome a {
        text-decoration: none;
    }
    #page .welcome a:hover {
        text-decoration: underline;
    }
    #page .welcome h1, #page .welcome h2, #page .welcome h3, #page .welcome h4 {
        background-image: url(/static/img/80_trans_white_bg.png);
        background-repeat: repeat;
        width: auto;
        float: right;
        padding: 0 0.25em 0 0.25em;
    }
    #page .welcome h1 {
        padding: 0.1em 0.25em 0.1em 0.25em;
    }
    #page .welcome h3 {
        padding: 0.2em 0.3em 0.25em 0.3em;
        margin-top: -1em;
    }
    #page .welcome .searchbox * {
        vertical-align: middle;
    }
    #page .welcome .searchbox input {
        margin-top: 0.4em;
    }

3. The CSS file references two images -- ``/static/img/80_trans_white_bg.png`` and
``/front_page/_files/welcome.jpg``.   The ``welcome.jpg`` image can be
added simply by uploading a file named ``welcome.jpg`` to the Front
Page.  You'll want to copy 
`80_trans_white_bg.png <https://dentonwiki.org/static/img/80_trans_white_bg.png>`_
to ``/usr/share/localwiki/static/img`` (or
``env/share/locawiki/static/img`` for manual installations)

4. Now we want to reference this new ``denton.css`` file from the HTML
of all the pages.  Let's go into our local template directory,
``/usr/share/localwiki/templates/`` and create the file
``site/extra_media.html`` and then we add the extra CSS into the file::

  <link rel="stylesheet" href="{{ STATIC_URL }}css/denton.css?v=1">

Then we save the file and restart the webserver::

    sudo /etc/init.d/apache2 restart

and we'll have the ``denton.css`` file referenced on all our pages!


Creating an entirely new theme
------------------------------

After a certain amount of customization it may make sense to create an
entirely new theme.  Here's how you'd go about doing this:

1. Go into the localwiki code directory, referenced in the beginning of
Example 1, and copy the ``sapling`` theme directory to your global
``themes`` directory::

    $ cd /path/to/localwiki/code/directory
    $ cd themes/
    $ cp -r sapling /usr/share/localwiki/themes/nameofyourtheme

.. note:: In localwiki-0.12-beta-12 there wasn't a ``themes`` directory
   in share/localwiki.  Create it if it's missing.

Then edit the ``/usr/share/localwiki/conf/localsettings.py`` file and change the
``SITE_THEME`` value from ``sapling`` to ``nameofyourtheme``.

Then simply run::

    localwiki-manage collectstatic

and restart the webserver::

    /etc/init.d/apache2 restart

and the site will be using your new theme.

As you develop your theme you'll need to restart the
webserver whenever you change the ``templates/`` and run
``localwiki-manage collectstatic`` whenever you change the ``assets/``.


Referring to static assets in templates
---------------------------------------

Your theme templates can refer to static assets like this::

    <img src="{{STATIC_URL}}theme/img/mybutton.png"/>

That will pull up the file that lives at themes/yourtheme/img/mybutton.png.

Overriding built-in templates
-----------------------------

More detail on this soon.  You'll probably be able to figure this out if
you dig around.  But, as an example, to override ``pages/base.html``, you
simply define ``themes/nameofyourtheme/templates/pages/base.html``
