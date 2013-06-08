===============================================
``versionutils.merging``
===============================================

``django-versionutils``' ``merging`` app is very small.  So small, in
fact, that it currently consists only of a single class.  But we'll add
more as we develop things.

The goal of the `merging` app is to contain all logic for merging and
locking of models, forms, etc.

How to Install
==============

Simply add this project to your list of ``INSTALLED_APPS`` in
``settings.py``::

    INSTALLED_APPS = (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        ...
        'versionutils.merging',
        ...
    )

*********************************
:mod:`versionutils.merging.forms`
*********************************

.. autoclass:: versionutils.merging.forms.MergeMixin
