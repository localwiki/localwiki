=================
API Documentation
=================

LocalWiki provides a RESTful, read/write API with advanced geospatial
capabilities.  Reading (using ``GET`` requests) is allowed for all users,
but to write (``POST``, ``PUT``, ``PATCH``, ``DELETE``) you'll need to :ref:`generate an API key <apikey>`.

The LocalWiki API follows the conventions of `Tastypie <https://github.com/toastdriven/django-tastypie>`_.  If this documentation seems incomplete, refer to Tastypie's page on `Interacting with the API <http://django-tastypie.readthedocs.org/en/latest/interacting.html>`_ to become familiar with the common idiom.

.. note::

    You will probably want to try these URLs in your browser. In order to make them work in a browser, you'll need to append the ``format`` query string parameter.  For example, to view the `page` resource list, you'll want visit a URL like this::

    /api/page/?format=json

Unless otherwise specified, all endpoints that return lists support the ``limit`` and ``offset`` parameters for pagination. Pagination information is contained in the embedded ``meta`` object within the response.

Many list endpoints also support ordering by certain fields. Order-by fields
are listed for each resource.


API versioning
==============

The LocalWiki API sends API version information in the ``Content-type``
header.  For instance, ``Content-Type: application/vnd.api.v1+json; charset=utf-8``

You can lock your application to a particular version of the
API by sending an ``Accept`` header with an appropriate version string.
For instance, ``Accept: application/vnd.api.v1+json`` will request
version 1 of the API.


Formats
=======

This documentation gives examples in ``json``.  However, the API also supports the ``xml``, ``yaml``, ``jsonp``, and ``plist`` (binary plist) formats.  The ``jsonp`` format takes an optional ``callback`` querystring.


API Examples & Tools
====================

To get a handle on how to interact with the API, and how to
use the filtering system, see the `api examples <api_examples>`_.

.. toctree::
   :maxdepth: 1

   api_examples
   api_tools


Resources
=========

Site
----

The Site object can be queried to retrieve information about the LocalWiki instance.

Example Site object:

.. code-block:: javascript

        {
            "domain": "TallahasseeWiki.org", 
            "id": 1, 
            "language_code": "en-us", 
            "license": "<p>Except where otherwise noted, this content is licensed under a <a rel=\"license\" href=\"http://creativecommons.org/licenses/by/3.0/\">Creative Commons Attribution License</a>. See <a href=\"/Copyrights\">Copyrights.</p>", 
            "name": "TallahasseeWiki.org", 
            "resource_uri": "/api/site/1/", 
            "signup_tos": "I agree to release my contributions under the <a rel=\"license\" href=\"http://creativecommons.org/licenses/by/3.0/\" target=\"_blank\">Creative Commons-By license</a>, unless noted otherwise. See <a href=\"/Copyrights\" target=\"_blank\">Copyrights</a>.", 
            "time_zone": "America/Chicago"
        }

Schema
~~~~~~

::

    /api/site/schema/

List
~~~~~~

::

    /api/site/

Fetch
~~~~~~

::

    /api/site/[id]


Users
-----

User objects can be queried to retrieve information about LocalWiki users. Emails, passwords, etc are not included in responses.

Example User object:

.. code-block:: javascript

    {
        "date_joined": "2012-06-13T12:10:52", 
        "first_name": "Tanya", 
        "last_name": "Schaad", 
        "resource_uri": "/api/user/25/", 
        "username": "TanyaS"
    }


Schema
~~~~~~

::

    /api/user/schema/

List
~~~~

::

    /api/user/

Order by: ``username``, ``first_name``, ``last_name``, ``date_joined``

::

    /api/user/?order_by=date_joined

Fetch
~~~~~

::

    /api/user/[id]



Pages
-----

Pages are the base objects in a LocalWiki.  Pages contain, among other
things, a ``content`` field consisting of a special subset of HTML5
markup.

Example Page object:

.. code-block:: javascript

    {
        "content": "<p>Bradfordville Blues Club experience is like no other. It combines a truly unique location and atmosphere with the best the Blues has to offer. </p>",
        "id": 158, 
        "map": "/api/map/Bradfordville_Blues_Club", 
        "name": "Bradfordville Blues Club", 
        "page_tags": "/api/page_tags/Bradfordville_Blues_Club", 
        "resource_uri": "/api/page/Bradfordville_Blues_Club", 
        "slug": "bradfordville blues club"
    }

Schema
~~~~~~

::

    /api/page/schema/

List
~~~~

::

    /api/page/

Order by: ``name``, ``slug``

::

    /api/page/?order_by=name

Fetch
~~~~~

::

    /api/page/[name]

Create
~~~~~~

To create a new page, POST a JSON document containing at least the ``name`` and ``content`` properties to /api/page/. Other properties such as ``map`` may also be set.


Update
~~~~~~

To update an existing page, PUT a JSON document containing all the resource attributes to /api/page/[name].  You may also update a single field in a page by issuing a PATCH to /api/page/[name] with just the relevant field (e.g. ``content``).


Delete
~~~~~~

To delete an existing page, issue a DELETE to /api/page/[name].


More API Examples for Pages
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:ref:`api_examples_page`


Files
-----

Files are binary objects associated with a a given page.  Unlike other
resources, a ``file`` is connected to a page through its ``slug``
field, which specifies the ``slug`` of the ``page`` it is connected to.

Example File object:

.. code-block:: javascript

   {
        "file": "/media/pages/files/jvxvjj8xl9wehwma.jpg", 
        "id": 2, 
        "name": "my_headshot.jpg", 
        "resource_uri": "/api/file/2/", 
        "slug": "golden gate park"
    }


Schema
~~~~~~

::

    /api/file/schema/

List
~~~~

::

    /api/file/

Order by: ``name``, ``slug``

::

    /api/file/?order_by=slug

Fetch
~~~~~

::

    /api/file/[id]

Create
~~~~~~

To create a new file, POST a ``multipart/form-data`` form to
``/api/file/`` with form fields ``name`` (the filename), ``slug`` (the
``slug`` of the page the file should be attached to) and a field named
``file`` containing the file data.

Update
~~~~~~

To update an existing file, PUT a ``multipart/form-data`` form to
``/api/file/[id]/`` with form fields ``name`` (the filename), ``slug`` (the
``slug`` of the page the file should be attached to) and a field named
``file`` containing the file data.



Delete
~~~~~~

To delete an existing file, issue a DELETE to ``/api/file/[id]/``.


More API Examples for Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:ref:`api_examples_file`


Maps
----

Maps are collections of geographic data that are associated with a given
page.  Maps contain ``points``, ``lines``, and ``polys`` fields, each
containing `GeoJSON <http://en.wikipedia.org/wiki/GeoJSON>`_
(or an XML/format-specific equivalent).  Maps also contain a ``length``
field, which you do not need to manually provide when issuing POSTs.

The ``geom`` field is a collection of the
``points``, ``lines`` and ``polys`` fields.  Sometimes it's convient to
use this all-in-one field, though we cannot filter using the ``geom``
field.

Example Map object:

.. code-block:: javascript

    {
        "geom": {
            "geometries": [
                {
                    "coordinates": [
                        -84.292406, 
                        30.448938999999999
                    ], 
                    "type": "Point"
                }
            ], 
            "type": "GeometryCollection"
        }, 
        "id": 2, 
        "length": 0.0, 
        "lines": null, 
        "page": "/api/page/IFS_Business_Interiors", 
        "points": {
            "coordinates": [
                [
                    -84.292406, 
                    30.448938999999999
                ]
            ], 
            "type": "MultiPoint"
        }, 
        "polys": null, 
        "resource_uri": "/api/map/IFS_Business_Interiors"
    }

Schema
~~~~~~

::

    /api/map/schema/

List
~~~~

::

    /api/map/

Parameters
__________

full

* `False`: (default) pages for maps are returned as links
* `True`: pages for maps are returned in full (see `Pages`_ example object)

Fetch
~~~~~

::

    /api/map/[pagename]

Create
~~~~~~

To create a new map, POST a JSON document containing at least a ``geom`` attribute and a ``page`` attribute.  ``geom`` should be a `GeoJSON GeometryCollection <http://geojson.org/geojson-spec.html>`_ and ``page`` should be an api-relative URI of a ``page`` resource.  Instead of providing the ``geom`` attribute you may instead provide one or more of the ``points`` (MultiPoint), ``lines`` (MultiLineString) and ``polys`` (MultiPolygon) properties.

Update
~~~~~~

To update an existing map, PUT a JSON document containing all the resource attributes to /api/map/[pagename].  You may also update a single field in a page by issuing a PATCH to /api/map/[pagename] with just the relevant field (e.g. ``points``).


Delete
~~~~~~

To delete an existing map, issue a DELETE to /api/map/[pagename].


More API Examples for Maps
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:ref:`api_examples_map`


Tags
----

Tags are simple keywords associated with pages.  With tags, there are
two resources you'll be interested in using:  ``tag`` and
``page_tags``.  The ``tag`` resource represents the global *tag*
that may be used on many different pages.  ``page_tags`` are the tags
associated with a particular page.

A ``tag`` is represented by a ``name`` and a ``slug`` (name without
spaces and other characters).

Example Tag object:

.. code-block:: javascript

    {
        "id": 71, 
        "name": "coffee shop", 
        "resource_uri": "/api/tag/coffeeshop/", 
        "slug": "coffeeshop"
    }

Schema
~~~~~~

::

    /api/tag/schema/

List
~~~~

::

    /api/tag/

Order by: ``name``, ``slug``

::

    /api/tag/?order_by=name

Fetch
~~~~~

::

    /api/tag/[slug]

Create
~~~~~~

To create a new ``tag``, POST a JSON document containing at least a
``name`` attribute to /api/tag/.

Update
~~~~~~

You cannot currently update a tag.


Delete
~~~~~~

You cannot currently delete a tag.


More API Examples for Tags
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:ref:`api_examples_tag`


Page Tags
---------

``page_tags`` are the particular set of ``tags`` associated with a given
``page``.

A ``page_tags`` resource is represented by a ``page`` API URI and a ``tags``
attribute, which is a list of ``tag`` URIs.

Example PageTags object:

.. code-block:: javascript

    {
        "id": 2, 
        "page": "/api/page/Lake_Ella", 
        "resource_uri": "/api/page_tags/Lake_Ella", 
        "tags": [
            "/api/tag/lakes/", 
            "/api/tag/parks/", 
            "/api/tag/recreation/"
        ]
    }


Schema
~~~~~~

::

    /api/page_tags/schema/

List
~~~~

::

    /api/page_tags/

Order by: ``page``, ``tags``

::

    /api/page_tags/?order_by=page

Fetch
~~~~~

::

    /api/page_tags/[pagename]

Create
~~~~~~

To create a new ``page_tags`` set, POST a JSON document containing at least a
``page`` attribute (path to a ``page`` resource) and a ``tags``
attribute (a list of paths to ``tag`` resources).

**Note** that all the ``tag`` resources you specify **must already exist**.
If they don't exist yet you'll want to create them first with a POST to
the ``tag`` endpoint.

Update
~~~~~~

To update an existing ``page_tags`` set, PUT a JSON document all the
resource attributes to /api/page_tags/[pagename].

**Note** that all the ``tag`` resources you specify **must already exist**.
If they don't exist yet you'll want to create them first with a POST to
the ``tag`` endpoint.

Delete
~~~~~~

To delete a ``page_tags`` set, issue a DELETE to
/api/page_tags/[pagename].


Historical resources
--------------------

All versioned resources have a corresponding ``*_version``
resource.  This resource has all of the fields of the original resource
but also has version-related fields.  These version-related fields are:

    * ``history_comment`` - the comment made by the user when the resource was saved.
    * ``history_date`` - the date the resource was saved.  In `ISO-8601 format <http://en.wikipedia.org/wiki/ISO_8601>`_.
    * ``history_type`` - the *type* of change that was made.  Valid options are:

      * ``0`` - Added
      * ``1`` - Updated
      * ``2`` - Deleted
      * ``3`` - Deleted through a foreign key cascade
      * ``4`` - Reverted
      * ``5`` - Reverted/Added
      * ``6`` - Reverted/Deleted
      * ``7`` - Reverted/Deleted via cascade
      * ``8`` - Reverted via cascade
    * ``history_user`` - the user who made the change. If this is ``null`` then this edit was made while not logged in.
    * ``history_user_ip`` - the IP address of the user who made the change
    * ``history_id`` - not really useful, you should feel free to ignore this. This is the per-resource-class (not instance) history id.


.. _apikey:

Generating an API key
=====================

Currently, you'll need to generate an API key before you can write to
the API.  **Be careful who you give an API key to**, because there are
currently no API limits in place.  To create or revoke an API key, simply
visit the :doc:`administrative interface <settings>` and the "Api keys" area:

.. figure:: /_static/images/admin_apikey_1.png

and then click "Add api key" and fill out the form. Pick the user you'd
like to have an API key, leave the "Key" field blank and save:

.. figure:: /_static/images/admin_apikey_2.png

then you can copy the created Key and pass it along to the user:

.. figure:: /_static/images/admin_apikey_3.png


Using the API key
-----------------

To use the API key, send an ``Authorization`` header along with your
request.  The format is ``Authorization: ApiKey <username>:<api_key>``.
E.g.::

    Authorization: ApiKey daniel:204db7bcfafb2deb7506b89eb3b9b715b09905c8

Some webservers may be configured to block the ``Authorization`` header.
In that case, simply send a request with a querystring containing a
``username`` and an ``api_key`` attribute, e.g.::

    /api/page/?username=daniel&api_key=204db7bcfafb2deb7506b89eb3b9b715b09905c8

The header approach is perfered, though.  If the header approach isn't
working and you're running Apache be sure that you have the ``WSGIPassAuthorization On``
directive in your apache configuration.  See the :doc:`web server
configuration docs <configure>` for an
example.
