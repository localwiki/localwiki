=====
Notes
=====

Migrations / syncdb
-------------------
Each versioned model has a corresponding ``*_hist`` table.  So when you change the schema of models you have versioned you'll need to execute similar SQL / migrations on the history tables as your model tables.

For instance:

Model ``Member`` is stored in my ``members_member`` table.  I'd normally run
(postgres, adjust accordingly)
``ALTER TABLE members_member ADD COLUMN newcolumn varchar(10);``
Because the members object is set to be versioned, I'll also want to run
``ALTER TABLE members_member_hist ADD COLUMN newcolumn varchar(10);``

I haven't used any of the automated Django schema migration utilities, but I assume they will either 1) work automatically, as they will detect the schema change or 2) need a bit of direction to do whatever they do to the base model to the versioned model as well.

Because there's no magic here -- there's really a separate ``_hist`` table for each of your model's tables with all the same fields, migrations should be straightforward.

Bulk QuerySet update() / Admin bulk actions
-------------------------------------------
The ``versioning`` app works fine with ``QuerySet.delete()`` and the admin's bulk deleting.  However, at the moment there's no way to have it work with ``QuerySet.update()``.  We recommend not using ``QuerySet.update()`` on models you want to perserve versioning information on.

Working around this is braindead-easy!  See http://code.trac.localwiki.org/ticket/33 for a workaround.  Issuing a ``QuerySet.update()`` won't break anything -- it just won't save a new version of the model in the history.

For more information, see Django ticket #12184 (http://code.djangoproject.com/ticket/12184), #10754 (http://code.djangoproject.com/ticket/10754) and our ticket #33 (http://code.trac.localwiki.org/ticket/33).  Weigh in!

Smart lookups
-------------

We try do our best to be smart about unique fields! For instance, if you delete and then recreate a model (so it has a new integer primary key), we'll still pull up the correct history of the model based on its unique fields, if possible.

However, if you rename a unique field on a model you'll notice that it will clear out the history of the model unless there was a model with that same field in the past (in which case you'll see that model's history). If you'd like to rename all the historical versions' unique fields you'll want to do that by hand, kinda like this::

    >>> p.name = "New name!"
    # 'name' is a unique field
    >>> for p_h in p.history.all():
    >>>     p_h.name = "New name!"
    >>>     p_h.save(track_changes=False)
    >>> p.save()

SQLite bug
----------

Running SQLite?  If you delete a model that contains no unique fields
we'll zero out all its history.  This is to prevent corruption.

http://code.djangoproject.com/ticket/10164 is the reason we have to do
this.

Workaround: Don't use SQLite in production, or if you do just know that when you
delete models that don't have unique fields it may be "for good."
