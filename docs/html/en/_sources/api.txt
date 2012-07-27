=================
API Documentation
=================

LocalWiki provides a RESTful, read/write API with advanced geospatial
capabilities.  Reading (using ``GET`` requests) is allowed for all users,
but to write (``POST``, ``PUT``, ``PATCH``, ``DELETE``) you'll need to generate an API
key.

The LocalWiki API follows the conventions of `Tastypie <https://github.com/toastdriven/django-tastypie>`_.  If this documentation seems incomplete, refer to Tastypie's page on `Interacting with the API <http://django-tastypie.readthedocs.org/en/latest/interacting.html>`_ to become familiar with the common idiom.

.. note::

    You will probably want to try these URLs in your browser. In order to make them work in a browser, you'll need to append the ``format`` query string parameter.  For example, to view the `page` resource list, you'll want visit a URL like this::

    /api/page/?format=json

Unless otherwise specified, all endpoints that return lists support the ``limit`` and ``offset`` parameters for pagination. Pagination information is contained in the embedded ``meta`` object within the response.


API versioning
==============

The LocalWiki API sends API version information in the ``Content-type``
header.  For instance, ``Content-Type: application/vnd.api.v1+json; charset=utf-8``

You can lock your application to a particular version of the
API by sending an ``Accept`` header with an appropriate version string.
For instance, ``Accept: application/vnd.api.v1+json`` will request
version 1 of the API.


API structure
==============

blah blah REST self-describing.

Site
====

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
------

::

    http://localhost:8000/api/site/schema/

List
----

::

    http://localhost:8000/api/site/

Fetch
-----

::

    http://localhost:8000/api/site/[id]/


Users
=====

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
------

::

    http://localhost:8000/api/user/schema/

List
----

::

    http://localhost:8000/api/user/

Fetch
-----

::

    http://localhost:8000/api/user/[id]/



Pages
=====

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
------

::

    http://localhost:8000/api/page/schema/

List
----

::

    http://localhost:8000/api/page/

Fetch
-----

::

    http://localhost:8000/api/page/[name]/

Create
------

To create a new page, POST a JSON document containing at least the ``name`` and ``content`` properties to /api/page/. Other properties such as ``map`` may also be set.


Update
------

To update an existing page, PUT a JSON document containing all the resource attributes to /api/page/[name].  You may also update a single field in a page by issuing a PATCH to /api/page/[name] with just the relevant field (e.g. ``content``).


Delete
------

To delete an existing page, issue a DELETE to /api/page/[name].



Contents:

.. toctree::
   :maxdepth: 1

   api_examples
