Permissions
===========

LocalWiki uses a pretty flexible system of permissions that allows the
administrator to say who is allowed to add, change, and delete different
objects (pages, maps, files, etc.).  It also lets the administrator ban users
who are malicious.

There are two levels of permissions: by type of object (i.e., page, map, etc.)
and by specific object (i.e., "Front Page").  This allows you to set the
default permissions for all objects and still adjust them for certain objects
that should be more protected (or more open).


Users and groups
----------------

Users can belong to one or more Group, and new groups can be added any time.
You can grant permissions to each group, and the users in that group will
inherit those permissions.  This makes role-based permissions possible,
allowing you, for example, to create a group called "Trusted Users" and give
this group additional permissions.

.. note::

   It is good practice to grant permissions to groups instead of individual
   users because it's more manageable (there are lots of users and few groups)
   and maintainable (users come and go, and it's much easier to add and remove
   them from groups as needed).


If you followed the installation instructions, you should have the following
groups out of the box:

.. figure:: /_static/images/admin_groups.png

``Anonymous``
    This group contains ``AnonymousUser``, which is used to set permissions for
    people who are not logged in.

``Authenticated``
    This group contains every user except ``AnonymousUser``.  New users are
    automatically added to this group.  It's a catch-all group to make it easy
    to set the default settings for everyone who's logged in.

``Banned``
    Users added to this group will be denied all permissions, regardless of
    what permissions are set for this group or what other groups they belong
    to.


Banning a user
--------------

To ban a user, simply add the user to the ``Banned`` group.  You do not need
to remove the user from other groups.  Any user in the ``Banned`` group will
not have any permissions.

First, find the user in the admin interface, using the search box:

.. figure:: /_static/images/admin_user_search.png

Click on the username, and scroll down "Groups" section. Hold down
"Control" ("Command" on a Mac) while selecting ``Banned`` group, and press
"Save".

.. figure:: /_static/images/admin_ban_user.png

.. note::

   While it's possible in the admin interface to delete a user, this is
   **NOT** recommended as it will also delete every change the user has made.
   If you need to disable a user's account, it's best to just unmark the
   "active" checkbox for that user.


Adding a new administrator
--------------------------

To add a new administator, go pull up a user account in the *Users*
area, check both the *Staff status* and *Superuser status* checkboxes,
and save.

.. figure:: /_static/images/admin_add_new_admin.png

.. warning::

   Be care about who you set as an administrator.  By default,
   administrators can permanently delete data.  Also, **be sure that all
   admins have strong passwords**, otherwise someone may hijack their
   account and do evil things!

   You can selectively add more granular permissions in the *User
   permissions* area.


Setting permissions for specific objects
----------------------------------------

If you view a Page in the admin interface and then click "Object permissions"
you can then enter a group name and select which permissions the given group
should have for that specific Page.  Only those groups you choose will be able
to add, edit, and delete the Page.

Say, for example, you want to lock down a page so that only logged-in users
can edit it.  First, find the page in the admin interface and click on
"Object permissions" in the top right.

.. figure:: /_static/images/admin_page_permissions1.png

Then in the Groups section enter "Authenticated" and click "Manage group".

.. figure:: /_static/images/admin_page_permissions2.png

Click the "Choose all" button and press "Save".

.. figure:: /_static/images/admin_page_permissions3.png

Now, only those users who have logged in will be able to edit this page.

To clear out per-object permissions and go back to the defaults, on the
"Object permissions" screen click "edit" next to each group and clear out all
permissions.  When there are no groups or users shown on the "Object
permissions" screen, the application will look at the default permissions for
that object type.


Setting default permissions
---------------------------

When per-object permissions are not set for an object, the permissions backend
looks at what permissions the user has (either directly or through the groups
to which the user belongs) for that type of object.

If needed, you can set these permissions through the admin interface.  Edit
each group and select which default permissions the group should have.

Editing all of your group permissions by hand can be a lot to manage, so we
provide a setting you can modify in ``settings.py`` and a command to apply
them.  At the time of writing this, the setting looks like this::

    USERS_DEFAULT_PERMISSIONS = {'auth.group':
                                 [{'name': USERS_DEFAULT_GROUP,
                                   'permissions':
                                     [['add_mapdata', 'maps', 'mapdata'],
                                      ['change_mapdata', 'maps', 'mapdata'],
                                      ['delete_mapdata', 'maps', 'mapdata'],
                                      ['add_page', 'pages', 'page'],
                                      ['change_page', 'pages', 'page'],
                                      ['delete_page', 'pages', 'page'],
                                      ['add_pagefile', 'pages', 'pagefile'],
                                      ['change_pagefile', 'pages', 'pagefile'],
                                      ['delete_pagefile', 'pages', 'pagefile'],
                                      ['add_redirect', 'redirects', 'redirect'],
                                      ['change_redirect', 'redirects', 'redirect'],
                                      ['delete_redirect', 'redirects', 'redirect'],
                                     ]
                                  },
                                  {'name': USERS_ANONYMOUS_GROUP,
                                   'permissions':
                                     [['add_mapdata', 'maps', 'mapdata'],
                                      ['change_mapdata', 'maps', 'mapdata'],
                                      ['delete_mapdata', 'maps', 'mapdata'],
                                      ['add_page', 'pages', 'page'],
                                      ['change_page', 'pages', 'page'],
                                      ['delete_page', 'pages', 'page'],
                                      ['add_pagefile', 'pages', 'pagefile'],
                                      ['change_pagefile', 'pages', 'pagefile'],
                                      ['delete_pagefile', 'pages', 'pagefile'],
                                      ['add_redirect', 'redirects', 'redirect'],
                                      ['change_redirect', 'redirects', 'redirect'],
                                      ['delete_redirect', 'redirects', 'redirect'],
                                     ]
                                  },
                                 ]
                                }

You can edit this setting by adding or removing permissions for certain groups
or adding your own groups.  To apply these permissions (and overwrite the
previously set defaults), run the following command::

    localwiki-manage reset_permissions

.. note ::
   Regardless of everything said in this section, administrators and superusers
   are always granted all permissions, no matter what groups they are in or
   even whether they are in the ``Banned`` group.
