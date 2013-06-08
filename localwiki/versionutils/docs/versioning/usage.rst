=====
Usage
=====

Basic example
-------------

Using ``versionutils.versioning`` is extremely simple.  Here's a little usage example to get you started::

    >>> m = Person(name="Philip", description="Some dude")
    >>> m.save()
    # Save again with a new description.
    >>> m.description = "Just some guy"
    >>> m.save()
    # Look up the first historical version.
    >>> m_hist = m.versions.as_of(version=1)
    >>> m_hist
    <Person_hist: Person object as of 2011-02-15 17:23:20.483243>
    # The historical object has all the same attributes
    # as the original object.
    >>> m_hist.name
    u'Philip'
    >>> m_hist.description
    u'Some dude'

Historical instances have all the same fields as the normal model.  They
also have :attr:`the version_info field<version_info>` which has information on the
revision::

    >>> m_hist.version_info.date
    datetime.datetime(2011, 2, 15, 17, 23, 20, 483243)
    >>> m_hist.version_info.version_number()
    1

If you enable the :doc:`AutoTrackUserInfoMiddleware<install>` then the optional
``version_info.user`` and ``version_info.user_ip`` attributes be
automatically added.

Reverting objects
-----------------

Super-easy!  All you need to do is call ``revert_to()`` on the historical
instance::

    >>> m.description
    u'Just some guy'
    >>> m_hist = m.versions.as_of(version=1)
    >>> m_hist
    <Person_hist: Person object as of 2011-02-15 17:23:20.483243>
    >>> m_hist.revert_to()
    >>> m = Person.objects.get(name="Philip")
    >>> m.description
    u'Some dude'

Getting historical objects
--------------------------

Sometimes we just want the most recent historical instance.  Calling
``versions.most_recent()`` will do the trick::

    >>> m.versions.most_recent()
    <Person_hist: Person object as of 2011-02-15 23:48:09.507812>

We've seen ``as_of()`` already.  ``as_of()`` can also take a ``date``
parameter::

    >>> m.versions.as_of(date=datetime(2011, 2, 15, 17, 23, 20, 483243))
    <Person_hist: Person object as of 2011-02-15 17:23:20.483243>
    # The datetime doesn't have to be exact.  We will return the historical
    # instance that's most recent, moving backward in time.
    >>> m.versions.as_of(date=datetime(2011, 2, 15, 17, 23, 21))
    <Person_hist: Person object as of 2011-02-15 17:23:20.483243>

We can also do lookups on the *model class itself*.  This is especially
important if we don't have a model instance around -- say, if the model was
most recently deleted::

    >>> m2 = Person(name="Mike")
    >>> m2.save()
    >>> Person.vesions.all()
    [<Person_hist: Person object as of 2011-02-15 21:53:15.613445>, <Person_hist: Person object as of 2011-02-15 20:33:03.409725>, <Person_hist: Person object as of 2011-02-15 18:07:40.645975>, <Person_hist: Person object as of 2011-02-15 17:23:40.416443>, <Person_hist: Person object as of 2011-02-15 17:23:20.483243>]
    # We can also do a filter on all historical instances of the Person
    # model.
    >>> Person.versions.filter(name="Mike")
    [<Person_hist: Person object as of 2011-02-15 21:53:15.613445>]
    # And we can filter based on historical info attributes, too.
    >>> Person.versions.filter(version_info__date__gte=datetime(2011, 2, 15, 20))
    [<Person_hist: Person object as of 2011-02-15 21:53:15.613445>, <Person_hist: Person object as of 2011-02-15 20:33:03.409725>]

Smart related object lookup
---------------------------

When a versioned model is related to another versioned model via a foreign
key lookups of the related object on the historical instance will refer
to that related object *at the time the parent instance was saved*.  Here's an
example:

Suppose we have::

    class Profile(models.Model):
        details = models.TextField()
        person = models.ForeignKey(Person)
    
    versioning.register(Profile)

then::

    >>> philip = Person.objects.get(name='Philip')
    >>> profile = Profile(details="Long walks on the beach", person=philip)
    >>> profile.save()
    # Now we change the description on the related model.
    >>> philip.description = "Runs fast, writes code"
    >>> philip.save()
    # We get the most recent historical instance of the Profile object.
    >>> profile_hist = profile.versions.most_recent()
    # This gives us a historical instance of the Person model at the
    # correct point in time:
    >>> profile_hist.person
    <Person_hist: Person object as of 2011-02-15 20:33:03.409725>
    >>> profile_hist.person.description
    u'Some dude'
    # The older description is displayed!  Yay!

This works similarly for ``OneToOneField`` and ``ManyToManyField``.

Reverse lookups do the right thing, too!  Here's an example of a reverse
lookup::

    >>> bob = Person(name="Bob", description="Boring guy")
    >>> bob.save()
    >>> profile = Profile(details="Most boring", person=bob)
    >>> profile.save()
    >>> bob.description = "Actually not that boring"
    >>> bob.save()
    # At the time 'bob' was originally created, no Profiles were pointed to
    # him.  So if we do a reverse lookup on the original historical instance
    # we should expect to see no Profiles in the lookup.
    >>> bob_original = bob.versions.as_of(version=1)
    >>> bob_original.profile_set.all()
    []
    # If we do a lookup on the most recent historical instance, we should
    see the "Most boring" profile pointed at it.
    >>> bob_most_recent = bob.versions.most_recent()
    >>> for h in bob_most_recent.profile_set.all(): print h.details
    Most boring

So, a reverse lookup will find related objects that were pointed to the
current historical object *at the time it was saved!*

``OneToOneField`` and ``ManyToManyField`` behave similarly.

Passing in extra arguments to save() and delete()
-------------------------------------------------
Because we sometimes want to associate extra information with a given
model ``save()`` or ``delete()`` (like a save comment), we allow extra arguments
to be passed into ``save()`` and ``delete()``::

    >> p = Person(name="Arlen", description="Likes beer")
    >> p.save(comment="creating this person for the first time")
    >> ph = p.versions.most_recent()
    >> ph.version_info.comment
    u'creating this person for the first time'

You can pass in any of the *optional fields* on the :attr:`version_info
attribute<version_info>` into the ``save()`` and ``delete()`` methods on your
models.  In theory you can pass in non-optional fields (like ``date``),
but you probably won't need to do that.

Some more examples
------------------

Get all historical versions where the model was added, not just
updated::

    >>> from versionutils.versioning.constants import *
    >>> Person.versions.filter(version_info__type=TYPE_ADDED)
    [<Person_hist: Person object as of 2011-02-15 21:53:15.613445>,
     <Person_hist: Person object as of 2011-02-15 17:23:20.483243>]
