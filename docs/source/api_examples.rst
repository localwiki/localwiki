============
API Examples
============

.. _api_examples_page:

Page examples
-------------

Get all pages whose title ends in "park", case-insensitive
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``/api/page/?name__iendswith=park``

.. code-block:: javascript

  {
      "meta": {
          "limit": 20, 
          "next": null, 
          "offset": 0, 
          "previous": null, 
          "total_count": 4
      }, 
      "objects": [
          {
              "content": "<p>A park page!</p>",
              "id": "166", 
              "name": "Dorothy B. Oven Park", 
              "resource_uri": "/api/page/Dorothy_B._Oven_Park", 
              "slug": "dorothy b. oven park"
          }, 
          {
              "content": "<p>Another park page!</p>",
              "id": "108", 
              "name": "Winthrop Park", 
              "resource_uri": "/api/page/Winthrop_Park", 
              "slug": "winthrop park"
          }
      ]
  }

Alternatively, we could have filtered on the `slug` field, which is always lowercase:

``/api/page/?slug__endswith=park``


Find pages that contain the word 'cafe'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If we try to do something like:

``/api/page/?content__contains=cafe``

We get the message "The 'content' field does not allow filtering."  Instead, for full-text searches we'll want to use the ``/search/`` method on the `page` resource.  Search takes a query parameter, `q`, which is a URL-encoded search string.  E.g.:

``/api/page/search/?q=cafe``

.. code-block:: javascript

  {
      "objects": [
          {
              "content": "<p>MMm..caffeine!</p>",
              "id": "101", 
              "name": "Coffee", 
              "resource_uri": "/api/page/Coffee", 
              "slug": "coffee"
          }
      ]
  }

*Note*: You currently cannot use other filters on top of a `search` method.


Page versions
~~~~~~~~~~~~~

All versions of pages that were edited after a certain date
```````````````````````````````````````````````````````````

Let's find all versions of pages that were edited after June 25th, 2012 at 22:21:30 :

``/api/page_version/history_date__gte=2012-06-25T22:21:30``

.. code-block:: javascript

  {
      "meta": {
          "limit": 20, 
          "next": "/api/page_version/?history_date__gte=2012-06-25T22%3A21%3A30&offset=20&limit=20", 
          "offset": 0, 
          "previous": null, 
          "total_count": 34
      }, 
      "objects": [
          {
              "content": "<p>Tallahassee offers many options for your food shopping needs.</p>",
              "history_comment": null, 
              "history_date": "2012-07-11T19:18:22.103443", 
              "history_id": "786", 
              "history_type": 1, 
              "history_user": "/api/user/2",
              "history_user_ip": null, 
              "id": 89, 
              "name": "Groceries", 
              "resource_uri": "/api/page_version/786/", 
              "slug": "groceries"
          }, 
          {
              "content": "<p>Write anything you'd like about yourself here!</p>",
              "history_comment": null, 
              "history_date": "2012-07-11T00:30:05.415302", 
              "history_id": "785", 
              "history_type": 1, 
              "history_user": "/api/user/3",
              "history_user_ip": "127.0.0.1", 
              "id": 145, 
              "name": "BArmstrong", 
              "resource_uri": "/api/page_version/785/", 
              "slug": "barmstrong"
          }, 

          ...

          {
              "content": "<p><span class=\"image_frame image_left\"><img src=\"_files/CampWiki-logo-400.png\" style=\"width: 300px; height: 71px;\"></span></p>",
              "history_comment": "add shirt", 
              "history_date": "2012-06-26T10:15:14", 
              "history_id": "767", 
              "history_type": 1, 
              "history_user": "/api/user/4",
              "history_user_ip": "67.233.209.109", 
              "id": 54, 
              "name": "CampWiki", 
              "resource_uri": "/api/page_version/767/", 
              "slug": "campwiki"
          }
      ]
  }


All versions of pages that were edited after a certain date and have a certain title
````````````````````````````````````````````````````````````````````````````````````

Let's find all versions of pages that were edited after June 25th, 2012 at 22:21:30 and whose title ends with 'park':

``/api/page_version/?slug__endswith=park&history_date__gte=2012-06-25T22:21:30``

.. code-block:: javascript

  {
      "meta": {
          "limit": 20, 
          "next": null, 
          "offset": 0, 
          "previous": null, 
          "total_count": 4
      }, 
      "objects": [
          {
              "content": "<p><strong>Dorthy Oven Park</strong> is a <a href=\"http://example.org\">favorite</a> destination during the holiday season, decorated with a stunning display of holiday lights!</p>",
              "history_comment": "bold name", 
              "history_date": "2012-06-26T07:34:29", 
              "history_id": "756", 
              "history_type": 1, 
              "history_user": "/api/user/4",
              "history_user_ip": "67.233.209.109", 
              "id": 166, 
              "name": "Dorothy B. Oven Park", 
              "resource_uri": "/api/page_version/756/", 
              "slug": "dorothy b. oven park"
          }, 
          {
              "content": "<p>Dorthy Oven Park is a <a href=\"http://example.org\">favorite</a> destination during the holiday season, decorated with a stunning display of holiday lights!</p>",
              "history_comment": "add exclamation", 
              "history_date": "2012-06-26T07:33:45", 
              "history_id": "755", 
              "history_type": 1, 
              "history_user": "/api/user/4",
              "history_user_ip": "67.233.209.109", 
              "id": 166, 
              "name": "Dorothy B. Oven Park", 
              "resource_uri": "/api/page_version/755/", 
              "slug": "dorothy b. oven park"
          }, 
          {
              "content": "<p>Dorthy Oven Park is a <a href=\"http://example.org\">favorite</a> destination during the holiday season, decorated with a stunning display of holiday lights.</p>",
              "history_comment": "complete external weblinks", 
              "history_date": "2012-06-26T07:01:47", 
              "history_id": "754", 
              "history_type": 1, 
              "history_user": "/api/user/4",
              "history_user_ip": "67.233.209.109", 
              "id": 166, 
              "name": "Dorothy B. Oven Park", 
              "resource_uri": "/api/page_version/754/", 
              "slug": "dorothy b. oven park"
          }, 
          {
              "content": "<p>Dorthy Oven Park is a favorite destination during the holiday season, decorated with a stunning display of holiday lights.</p>",
              "history_comment": null, 
              "history_date": "2012-06-25T22:21:30", 
              "history_id": "753", 
              "history_type": 1, 
              "history_user": "/api/user/6",
              "history_user_ip": "67.233.187.55", 
              "id": 166, 
              "name": "Dorothy B. Oven Park", 
              "resource_uri": "/api/page_version/753/", 
              "slug": "dorothy b. oven park"
          }
      ]
  }


All pages tagged with [sometag]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``/api/page/?page_tags__tags__slug=sometag&format=json``


.. _api_examples_file:

File examples
-------------

Get all files on a given page
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's get all files on the 'Golden Gate Park' page.

``/api/file/slug=golden gate park``

.. code-block:: javascript

  {
      "meta": {
          "limit": 20, 
          "next": null, 
          "offset": 0, 
          "previous": null, 
          "total_count": 2
      }, 
      "objects": [
          {
              "file": "/media/pages/files/1bd1fgbitljt4egt.JPG", 
              "id": "94", 
              "name": "tacos.JPG", 
              "resource_uri": "/api/file/94/", 
              "slug": "golden gate park"
          }, 
          {
              "file": "/media/pages/files/qlwizj8dqkstrler.jpg", 
              "id": "93", 
              "name": "scruzmountainz.jpg", 
              "resource_uri": "/api/file/93/", 
              "slug": "golden gate park"
          }
      ]
  }

We can retrieve the file itself by visiting the location specified in
the `file` attribute.


.. _api_examples_map:

Map examples
------------

Get the map associated with a particular page
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's get the map data on the "Lake Ella" page.  We can just visit the
URI without any filtering:

``/api/map/Lake_Ella``

.. code-block:: javascript

  {
      "geom": {
          "geometries": [
              {
                  "coordinates": [
                      [ [-84.281762999999998, 30.462340000000001], ...  ]
                  ], 
                  "type": "Polygon"
              }
          ], 
          "type": "GeometryCollection"
      }, 
      "id": 1, 
      "length": 0.0121161205512, 
      "lines": null, 
      "page": "/api/page/Lake_Ella", 
      "points": null, 
      "polys": {
          "coordinates": [
              [[ [-84.281762999999998, 30.462340000000001], ...  ]]
          ], 
          "type": "MultiPolygon"
      }, 
      "resource_uri": "/api/map/Lake_Ella"
  }


Get all maps associated with pages ending in 'Park'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get all the map data for all pages whose title end in 'park':

``/api/map/?page__slug__endswith=park``

.. code-block:: javascript

  {
      "meta": {
          "limit": 20, 
          "next": null, 
          "offset": 0, 
          "previous": null, 
          "total_count": 3
      }, 
      "objects": [
          {
              "geom": {
                  "geometries": [
                      {
                          "coordinates": [
                              [ [-84.267825999999999, 30.466224], ...  ]
                          ], 
                          "type": "Polygon"
                      }
                  ], 
                  "type": "GeometryCollection"
              }, 
              "id": 20, 
              "length": 0.015599483822, 
              "lines": null, 
              "page": "/api/page/Winthrop_Park", 
              "points": null, 
              "polys": {
                  "coordinates": [
                      [[ [-84.267825999999999, 30.466224], ...  ]]
                  ], 
                  "type": "MultiPolygon"
              }, 
              "resource_uri": "/api/map/Winthrop_Park"
          }, 
          {
              "geom": {
                  "geometries": [
                      {
                          "coordinates": [-84.251131999999998, 30.449670000000001],
                          "type": "Point"
                      }
                  ], 
                  "type": "GeometryCollection"
              }, 
              "id": 21, 
              "length": 0.0, 
              "lines": null, 
              "page": "/api/page/Governor%27s_Park", 
              "points": {
                  "coordinates": [[-84.251131999999998, 30.449670000000001]], 
                  "type": "MultiPoint"
              }, 
              "polys": null, 
              "resource_uri": "/api/map/Governor%27s_Park"
          }, 
          {
              "geom": {
                  "geometries": [
                      {
                          "coordinates": [-84.254312999999996, 30.493468], 
                          "type": "Point"
                      }
                  ], 
                  "type": "GeometryCollection"
              }, 
              "id": 33, 
              "length": 0.0, 
              "lines": null, 
              "page": "/api/page/Dorothy_B._Oven_Park", 
              "points": {
                  "coordinates": [[-84.254312999999996, 30.493468]], 
                  "type": "MultiPoint"
              }, 
              "polys": null, 
              "resource_uri": "/api/map/Dorothy_B._Oven_Park"
          }
      ]
  }


Find all maps that contain a particular point
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's find all maps that contain a point that lies inside of Golden Gate
Park:

``/api/map/?polys__contains={"type": "Point", "coordinates": [-122.475233, 37.768617]}``

.. code-block:: javascript

  {
      "meta": {
          "limit": 20, 
          "next": null, 
          "offset": 0, 
          "previous": null, 
          "total_count": 1
      }, 
      "objects": [
          {
              "geom": {
                  "geometries": [
                      {
                          "coordinates": [
                              [ [-122.510948, 37.771121999999998], ...  ]
                          ], 
                          "type": "Polygon"
                      }
                  ], 
                  "type": "GeometryCollection"
              }, 
              "id": 36, 
              "length": 0.12849756341900001, 
              "lines": null, 
              "page": "/api/page/Golden_Gate_Park", 
              "points": null, 
              "polys": {
                  "coordinates": [
                      [[ [-122.510948, 37.771121999999998], ...  ]]
                  ], 
                  "type": "MultiPolygon"
              }, 
              "resource_uri": "/api/map/Golden_Gate_Park"
          }
      ]
  }

As expected, we get back the map for Golden Gate Park.


Find all maps inside of a region
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's find all maps inside of a polygon region roughly representing the
United States.

Due to technical limitations, we can only query for one geometry type
(points, lines or polygons) at a time.  So we query for each in
succession.

First, let's find the points that lay inside:

``/api/map/?points__within={ "type": "Polygon", "coordinates": [[[-125.363617, 48.656273], [-123.254242, 31.608656], [-77.902679, 26.068811], [-65.597992, 44.301984], [-125.363617, 48.656273]]]}``

Then the lines:

``/api/map/?lines__within={ "type": "Polygon", "coordinates": [[[-125.363617, 48.656273], [-123.254242, 31.608656], [-77.902679, 26.068811], [-65.597992, 44.301984], [-125.363617, 48.656273]]]}``

Finally, the polygons:

``/api/map/?polys__within={ "type": "Polygon", "coordinates": [[[-125.363617, 48.656273], [-123.254242, 31.608656], [-77.902679, 26.068811], [-65.597992, 44.301984], [-125.363617, 48.656273]]]}``

Here are the results:

With points within:

.. code-block:: javascript

  {
      "meta": {
          "limit": 20, 
          "next": null, 
          "offset": 0, 
          "previous": null, 
          "total_count": 19
      }, 
      "objects": [
          {
              "geom": {
                  "geometries": [
                      {
                          "coordinates": [-84.292406, 30.448938999999999], 
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
                  "coordinates": [[-84.292406, 30.448938999999999]], 
                  "type": "MultiPoint"
              }, 
              "polys": null, 
              "resource_uri": "/api/map/IFS_Business_Interiors"
          }, 
          ...
          {
              "geom": {
                  "geometries": [
                      {
                          "coordinates": [-84.281746999999996, 30.440351], 
                          "type": "Point"
                      }
                  ], 
                  "type": "GeometryCollection"
              }, 
              "id": 34, 
              "length": 0.0, 
              "lines": null, 
              "page": "/api/page/Users/Governors-Inn", 
              "points": {
                  "coordinates": [[-84.281746999999996, 30.440351]], 
                  "type": "MultiPoint"
              }, 
              "polys": null, 
              "resource_uri": "/api/map/Users/Governors-Inn"
          }
      ]
  }

With lines within:

.. code-block:: javascript

  {
      "meta": {
          "limit": 20, 
          "next": null, 
          "offset": 0, 
          "previous": null, 
          "total_count": 1
      }, 
      "objects": [
          {
              "geom": {
                  "geometries": [
                      {
                          "coordinates": [-84.280647000000002, 30.457765999999999], 
                          "type": "Point"
                      }, 
                      {
                          "coordinates": [
                              [-84.280647000000002, 30.457765999999999], 
                              [-84.280647000000002, 30.435493000000001]
                          ], 
                          "type": "LineString"
                      }
                  ], 
                  "type": "GeometryCollection"
              }, 
              "id": 3, 
              "length": 0.022272425525, 
              "lines": {
                  "coordinates": [[
                      [-84.280647000000002, 30.457765999999999], 
                      [-84.280647000000002, 30.435493000000001]
                  ]], 
                  "type": "MultiLineString"
              }, 
              "page": "/api/page/Springtime_Tallahassee", 
              "points": {
                  "coordinates": [[-84.280647000000002, 30.457765999999999]], 
                  "type": "MultiPoint"
              }, 
              "polys": null, 
              "resource_uri": "/api/map/Springtime_Tallahassee"
          }
      ]
  }

With polygons within:

.. code-block:: javascript

  {
      "meta": {
          "limit": 20, 
          "next": null, 
          "offset": 0, 
          "previous": null, 
          "total_count": 11
      }, 
      "objects": [
          {
              "geom": {
                  "geometries": [
                      {
                          "coordinates": [
                              [ [-84.281762999999998, 30.462340000000001], ... ]
                          ], 
                          "type": "Polygon"
                      }
                  ], 
                  "type": "GeometryCollection"
              }, 
              "id": 1, 
              "length": 0.0121161205512, 
              "lines": null, 
              "page": "/api/page/Lake_Ella", 
              "points": null, 
              "polys": {
                  "coordinates": [
                      [[ [-84.281762999999998, 30.462340000000001], ... ]]
                  ], 
                  "type": "MultiPolygon"
              }, 
              "resource_uri": "/api/map/Lake_Ella"
          }, 
          {
              "geom": {
                  "geometries": [
                      {
                          "coordinates": [
                              [ [-84.297866999999997, 30.43648], ... ]
                          ], 
                          "type": "Polygon"
                      }
                  ], 
                  "type": "GeometryCollection"
              }, 
              "id": 8, 
              "length": 0.0043480920960800003, 
              "lines": null, 
              "page": "/api/page/CollegeTown", 
              "points": null, 
              "polys": {
                  "coordinates": [
                      [
                          [ [-84.297866999999997, 30.43648 ], ... ]
                      ]
                  ], 
                  "type": "MultiPolygon"
              }, 
              "resource_uri": "/api/map/CollegeTown"
          }, 
      ]
  }


.. _api_examples_tag:

Tag examples
------------

Pages with a particular tag
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get all pages tagged with 'park':

``/api/page_tags/?tags__slug=park``

.. code-block:: javascript

  {
      "meta": {
          "limit": 20, 
          "next": null, 
          "offset": 0, 
          "previous": null, 
          "total_count": 9
      }, 
      "objects": [
          {
              "id": 20, 
              "page": "/api/page/Camellia_Christmas_at_Maclay_Gardens", 
              "resource_uri": "/api/page_tags/Camellia_Christmas_at_Maclay_Gardens", 
              "tags": [
                  "/api/tag/christmas/", 
                  "/api/tag/entertainment/", 
                  "/api/tag/families/", 
                  "/api/tag/holidays/", 
                  "/api/tag/park/"
              ]
          }, 
          {
              "id": 50, 
              "page": "/api/page/Dorothy_B._Oven_Park", 
              "resource_uri": "/api/page_tags/Dorothy_B._Oven_Park", 
              "tags": [
                  "/api/tag/park/", 
                  "/api/tag/recreation/"
              ]
          }, 
          ...
      ]
  }


Pages with a tag or another tag
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get all pages tagged with 'park' or 'food:

``/api/page_tags/?tags__slug__in=park,food``

.. code-block:: javascript

  {
      "meta": {
          "limit": 20, 
          "next": null, 
          "offset": 0, 
          "previous": null, 
          "total_count": 11
      }, 
      "objects": [
          {
              "id": 33, 
              "page": "/api/page/Banh_Mi_Palace", 
              "resource_uri": "/api/page_tags/Banh_Mi_Palace", 
              "tags": [
                  "/api/tag/food/", 
                  "/api/tag/foodtrucks/", 
                  "/api/tag/restaurants/"
              ]
          }, 
          {
              "id": 20, 
              "page": "/api/page/Camellia_Christmas_at_Maclay_Gardens", 
              "resource_uri": "/api/page_tags/Camellia_Christmas_at_Maclay_Gardens", 
              "tags": [
                  "/api/tag/christmas/", 
                  "/api/tag/entertainment/", 
                  "/api/tag/families/", 
                  "/api/tag/holidays/", 
                  "/api/tag/park/"
              ]
          }, 
          ...
      ]
  }


Geographic data for all pages with a particular tag
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

While we could iterate through a list of pages-with-a-particular-tag and
retrieve pages' maps individually, we can also do this in a single query
by tying together attributes across relations.

Because each `map` resource has a `page` resource attached to it, and
each `page` resource has a `page_tags` resource attached to it, we can
tie these all together to get what we want!

We know we can do ``/api/page_tags/?tags__slug=park`` to get all pages
with the tag `park`.  And so we can tie these all together, giving us:

``/api/map/?page__page_tags__tags__slug=park``

To retrieve all the geographic data for all pages tagged with 'park':

.. code-block:: javascript

  {
      "meta": {
          "limit": 20, 
          "next": null, 
          "offset": 0, 
          "previous": null, 
          "total_count": 8
      }, 
      "objects": [
          {
              "geom": {
                  "geometries": [
                      {
                          "coordinates": [-84.251379, 30.515999999999998], 
                          "type": "Point"
                      }
                  ], 
                  "type": "GeometryCollection"
              }, 
              "id": 19, 
              "length": 0.0, 
              "lines": null, 
              "page": "/api/page/Camellia_Christmas_at_Maclay_Gardens", 
              "points": {
                  "coordinates": [[-84.251379, 30.515999999999998]], 
                  "type": "MultiPoint"
              }, 
              "polys": null, 
              "resource_uri": "/api/map/Camellia_Christmas_at_Maclay_Gardens"
          }, 
          ...
      ]
  }


Pages with a particular tag inside a particular geographic region
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's get all pages tagged with 'park' inside of an area roughly equal
to San Francisco, California.

We know the `map` resource has an associated `page` resource as an
attribute, and the `page` resource has a `page_tags` resource.

We know we can do ``/api/page_tags/?tags__slug=park`` to get all pages
with the tag `park`.  And we can do ``/api/map/?polys__within=<geojson>``
to get all pages with polygons that are within the provided geojson.
And so we can tie these all together, giving us:

``/api/map/?page__page_tags__tags__slug=parks&polys__within=<geojson>``

Full detail:

``/api/map/?page__page_tags__tags__slug=parks&polys__within={"type": "Polygon", "coordinates": [[[-122.521248, 37.798391], [-122.397651, 37.817378], [-122.353020, 37.718590], [-122.504082, 37.701751], [-122.521248, 37.798391]]]}``

.. code-block:: javascript

  {
      "meta": {
          "limit": 20, 
          "next": null, 
          "offset": 0, 
          "previous": null, 
          "total_count": 1
      }, 
      "objects": [
          {
              "geom": {
                  "geometries": [
                      {
                          "coordinates": [
                              [ [-122.510948, 37.771121999999998 ], ... ]
                          ], 
                          "type": "Polygon"
                      }
                  ], 
                  "type": "GeometryCollection"
              }, 
              "id": 36, 
              "length": 0.12849756341900001, 
              "lines": null, 
              "page": "/api/page/Golden_Gate_Park", 
              "points": null, 
              "polys": {
                  "coordinates": [
                      [
                          [ [-122.510948, 37.771121999999998 ], ... ]
                      ]
                  ], 
                  "type": "MultiPolygon"
              }, 
              "resource_uri": "/api/map/Golden_Gate_Park"
          }
      ]
  }


.. _api_examples_redirect:

Redirect examples
-----------------

Get all redirects pointed at a particular page
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Find all the redirects that point to the page with the slug 'coffee':

``/api/redirect/destination__slug=coffee``

.. code-block:: javascript

  {
      "meta": {
          "limit": 20, 
          "next": null, 
          "offset": 0, 
          "previous": null, 
          "total_count": 2
      }, 
      "objects": [
          {
              "destination": "/api/page/Coffee", 
              "id": 6, 
              "resource_uri": "/api/redirect/coffee%20shops/", 
              "source": "coffee shops"
          },
          {
              "destination": "/api/page/Coffee", 
              "id": 7, 
              "resource_uri": "/api/redirect/cafes/", 
              "source": "cafes"
          }
      ]
  }
