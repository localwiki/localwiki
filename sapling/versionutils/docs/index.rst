.. django-versionutils documentation master file, created by
   sphinx-quickstart on Wed Feb 16 19:27:16 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

``versionutils.versioning``
===============================================

``django-versionutils``' ``versioning`` app is a smart and flexible versioning system for models.  Existing model versioning systems left much to be desired.  Major advantages over existing versioning systems are:

* Easy-to-use ORM access to historical model data.
* Supports relational fields and is *smart* about relational
  lookups.
* Stores model data in separate tables, one table for each versioned
  model.  Doesn't add book-keeping fields or crazy things to your models.
* Does not serialize model data.  Migrations aren't insane.
* Does smart lookup of old model versions, even if the model is
  currently deleted.  Tracks models by unique fields where possible.
* Easy to extend and add your own custom fields to versioned models.
* Supports several constructs important to real-world usage, like 
  "delete all newer versions when reverting" and "don't track changes for
  this save."  Allows per-save data, like a changeset comment, to be
  optionally passed into the parent model.
* Extensive test suite.
* Can optionally automatically track user information during saves.

How to Install
==============

First, add this project to your list of ``INSTALLED_APPS`` in
``settings.py``::

    INSTALLED_APPS = (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        ...
        'versiontutils.versioning',
        ...
    )

If you want to automatically track user information during saves, simply add
``AutoTrackUserInfoMiddleware`` to your middleware::

    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'versionutils.versioning.middleware.AutoTrackUserInfoMiddleware',
    )

Now you've got the app installed!  But you probably want to track changes on
some models, right?  Simply add ``TrackChanges()`` to a model you want to
version::

    from versionutils.versioning import TrackChanges
    
    class MyModel(models.Model):
        ...
    
        history = TrackChanges()

Then run ``manage.py syncdb`` and you're set!

.. toctree::
   :maxdepth: 2

   tutorial
   notes

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

