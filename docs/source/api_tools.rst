=========
API Tools
=========

It should be easy to interact with the API using any standard HTTP
library.

We'll give some specific interaction examples here.


Python
------

If you're using Python, we recommend you check out the small and
simple `slumber <https://github.com/dstufft/slumber/>`_ library,
which makes it really easy to work with RESTful APIs like the LocalWiki API.
Here's some examples using slumber with the LocalWiki API::

    import slumber
    api = slumber.API('http://detroitwiki.org/api/')
    username = 'myusername'
    api_key = 'apikey'
    
    # Get all pages
    api.page.get()
    
    # Find all pages whose page name starts with 'Detroit', case
    # insensitive:
    api.page.get(name__istartswith='detroit')
    
    # Get detail about a particular, known page
    api.page('Front Page')
    
    # Create a new page
    api.page.post({'name': 'My new page', 'content': '<p>Hello.</p>'},
        username=username, api_key=api_key)


Ruby
----

Work has begun on a Ruby API client.  Check it out at https://github.com/codeforseattle/localwiki_client.  It's in a very early stage at this point, so you may want to help with its development!
