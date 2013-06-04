==============
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
        'versionutils.versioning',
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
some models, right?  Simply register the model you want to version::

    from versionutils import versioning
    
    class MyModel(models.Model):
        ...
    
    versioning.register(MyModel)

Then run ``manage.py syncdb`` and you're set!
