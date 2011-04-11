=========
Reference
=========

***************************
The diff template tag
***************************

The easiest way to use the ``diff`` app is probably our super-simple
template tag.  Use it like this, in your templates::

    {% load diff_tags %}

    {% diff m1 m2 %}

You can also use it, just like :func:`diff()<versionutils.diff.diff>`, with historical instances as the
arguments.  Example::

    old = page.history.as_of(version=old)
    new = page.history.as_of(version=new)
    return direct_to_template(request, 'your_template.html',
        {'old': old, 'new': new})

Then in your template just do::

    {% diff old new %}

and you're set!

***************************
:mod:`versionutils.diff`
***************************

.. autofunction:: versionutils.diff.diff
.. autofunction:: versionutils.diff.register

.. autoclass:: versionutils.diff.BaseFieldDiff
.. autoclass:: versionutils.diff.BaseModelDiff
