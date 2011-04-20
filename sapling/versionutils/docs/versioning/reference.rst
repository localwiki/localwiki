=========
Reference
=========

******************************
:mod:`versionutils.versioning`
******************************

.. class:: TrackChanges()

    Add an instance of this class as an attribute on your models to
    track changes to the model.

    ``TrackChanges`` is a manager, so standard queryset functions like
    ``all()`` and ``filter()`` work.

    Please :doc:`read the usage documentation.<usage>`

    Example::

        from versionutils.versioning import TrackChanges
        
        class MyModel(models.Model):
            ...
        
            history = TrackChanges()
    
    Then run ``manage.py syncdb`` and you’re set!

    .. method:: most_recent()

        This method must be called via an instance of the model rather
        than from the class.  E.g. ``m.history.most_recent()`` rather
        than ``Model.history.most_recent()``.

        Returns:
            The most recent :ref:`historical record
            instance<historical-instance>`.

        Raises:
            DoesNotExist: Instance has no historical record. 
    
    .. method:: as_of([date=None][, version=None])

        This method must be called via an instance of the model rather
        than from the class.  E.g. ``m.history.as_of(..)`` rather
        than ``Model.history.as_of(..)``.

        Args:
            date: A datetime object.  The datetime doesn't have to be
                exact.  We will return the historical instance that's
                most recent, moving backward in time.
            version: An integer version number.

        Returns:
            A :ref:`historical record instance<historical-instance>` that
            represents the object as it was at the date or version number
            provided.

        Raises:
            DoesNotExist: Instance hasn't been created yet.
    
.. _historical-instance:

Historical instance
===================

Methods on :class:`TrackChanges` return either historical instances or
QuerySets of historical instances.

A historical instance represents a model at some point in time.  A historical model contains all the same fields, attributes and methods as the usual model, but also has some extra methods and historical metadata:

    .. method:: revert_to([delete_newer_versions=False][, \**kws]):

        Reverts to this version of the model.  Example::

            >> ph = p.history.as_of(..)
            >> ph.revert_to()

        Args:
            delete_newer_versions: If True, delete all versions in the
                history newer than this version.
            track_changes: If False, won't log *this revert* as an action in
                the history log.
            kws: Any other keyword arguments you want to pass along to the
                model save method.

    .. attribute:: history_info
    
        Historical metadata for the the historical model.  You can
        :doc:`easily define new fields to track here.<extend>`

        Built-in attributes are:

        .. attribute:: date

           `DateTimeField` representing the momement in time the historical
           instance references.

        .. method:: version_number()

           Returns the version number of the historical instance.

        .. method:: type_to_verbose()

           Returns a human-readable description of the type of action
           the historical instance refers to.  E.g. "Updated"

        Optional fields, on by default (see :doc:`how to extend<extend>`):

        .. attribute:: user

            Optional `UserField`.  Automatically set if you have
            `AutoTrackUserInfoMiddleware` enabled
            (see :doc:`how to install <install>`)

        .. attribute:: user_ip

            Optional `IPAddressField`.  Automatically set if you have
            `AutoTrackUserInfoMiddleware` enabled
            (see :doc:`how to install <install>`)

        .. attribute:: comment

            Optional `CharField` intended to be a user's description of
            the change action.

        Fields you probably don't need to use:
        
        .. attribute:: type

           An integer representing the type of action the historical
           instance refers to.  You should probably use
           :func:`type_to_verbose()`.

        .. attribute:: id

           A *global* historic id for the instance.  This is global for
           the whole historical model's table.  Use
           :func:`version_number()`, it's almost certainly what you
           want.

************************************
:mod:`versionutils.versioning.forms`
************************************

.. autoclass:: versionutils.versioning.forms.CommentMixin

************************************
:mod:`versionutils.versioning.views`
************************************

A set of class-based views that make working with versioned models a
little more generic.  These views are modeled after django's
class-based generic views.

.. autoclass:: versionutils.versioning.views.UpdateView

    .. method:: success_msg()

       Returns a string that gets sent to
       :mod:`django.contrib.messages`' :func:`add_message()` when the
       model is successfully saved.
       
.. autoclass:: versionutils.versioning.views.DeleteView

    .. method:: success_msg()

       Returns a string that gets sent to
       :mod:`django.contrib.messages`' :func:`add_message()` when the
       model is successfully deleted.

    .. attribute:: template_name_suffix

        By default this is `_confirm_delete`.

    .. attribute:: form_class

        By default this is `DeleteForm`, which can be found in
        `versioning.forms`.

.. autoclass:: versionutils.versioning.views.RevertView
    
    .. attribute:: template_name_suffix

        By default this is `_confirm_revert`.

    .. attribute:: form_class

        By default this is `RevertForm`, which can be found in
        `versioning.forms`.

.. class:: versionutils.versioning.views.HistoryView

    A subclass of django.views.generic.ListView.

    .. method:: get_queryset()

        You need to provide this method.  It should return a queryset
        containing historical instances.  For instance::

            def get_queryset(self):
                all_page_history = Page(slug=self.kwargs['slug']).history.all()
                # We set self.page to the most recent historical instance of the
                # page.
                self.page = all_page_history[0]
                return all_page_history

    .. attribute:: context_object_name
       
        By default this is `version_list`.

    .. attribute:: template_name_suffix
       
        By default this is `_history`.
    
    .. attribute:: revert_view_name

        By default we look for a view with the name
        `revert-<object name>`.  If you provide a string for
        `revert_view_name` we'll use that as our revert view.
