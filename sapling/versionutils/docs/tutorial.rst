========
Tutorial
========

Basic example
-------------

Using ``versionutils.versioning`` is extremely simple.  Here's a little usage example to get you started::

    >>> m = Person(name="Philip", description="Some dude")
    >>> m.save()
    # Save again with a new description.
    >>> m.description = "Just some guy"
    >>> m.save()
    # Look up the first historical version.
    >>> m_hist = m.history.as_of(version=1)
    >>> m_hist
    <Person_hist: Person object as of 2011-02-15 17:23:20.483243>
    # The historical object has all the same attributes
    # as the original object.
    >>> m_hist.name
    u'Philip'
    >>> m_hist.description
    u'Some dude'

The historical object has information about the version, too::

    >>> m_hist.history_info.date
    datetime.datetime(2011, 2, 15, 17, 23, 20, 483243)
    >>> m_hist.history_info.version_number()
    1

If you enable the ``AutoTrackUserInfoMiddleware`` then the optional
``history_info.user`` and ``history_info.user_ip`` attributes be
automatically added.

You can add extra history fields to ``history_info`` by subclassing
``TrackChanges`` and extending the ``get_extra_history_fields`` method.

Reverting objects
-----------------

Super-easy!  All you need to do is call ``revert_to()`` on the historical
instance.

>>> m.description
u'Just some guy'
>>> m_hist = m.history.as_of(version=1)
>>> m_hist
<Person_hist: Person object as of 2011-02-15 17:23:20.483243>
>>> m_hist.revert_to()
>>> m = Person.objects.get(name="Philip")
>>> m.description
u'Some dude'

Getting historical objects
--------------------------

Sometimes we just want the most recent historical instance.  Calling
``history.most_recent()`` will do the trick:

>>> m.history.most_recent()
<Person_hist: Person object as of 2011-02-15 23:48:09.507812>

We've seen ``as_of()`` already.  ``as_of()`` can also take a ``date``
parameter:

>>> m.history.as_of(date=datetime(2011, 2, 15, 17, 23, 20, 483243))
<Person_hist: Person object as of 2011-02-15 17:23:20.483243>
# The datetime doesn't have to be exact.  We will return the historical
# instance that's most recent, moving backward in time.
>>> m.history.as_of(date=datetime(2011, 2, 15, 17, 23, 21))
<Person_hist: Person object as of 2011-02-15 17:23:20.483243>

We can also do lookups on the *model class itself*.  This is especially
important if we don't have a model instance around -- say, if the model was
most recently deleted.

>>> m2 = Person(name="Mike")
>>> m2.save()
>>> Person.history.all()
[<Person_hist: Person object as of 2011-02-15 21:53:15.613445>, <Person_hist: Person object as of 2011-02-15 20:33:03.409725>, <Person_hist: Person object as of 2011-02-15 18:07:40.645975>, <Person_hist: Person object as of 2011-02-15 17:23:40.416443>, <Person_hist: Person object as of 2011-02-15 17:23:20.483243>]
# We can also do a filter on all historical instances of the Person
# model.
>>> Person.history.filter(name="Mike")
[<Person_hist: Person object as of 2011-02-15 21:53:15.613445>]
# And we can filter based on historical info attributes, too.
>>> Person.history.filter(history_info__date__gte=datetime(2011, 2, 15, 20))
[<Person_hist: Person object as of 2011-02-15 21:53:15.613445>, <Person_hist: Person object as of 2011-02-15 20:33:03.409725>]

Smart related object lookup
---------------------------

When a versioned model is related to another versioned model via a foreign
key [#]_ lookups of the related object on the historical instance will refer
to that related object *at the time the parent instance was saved*.  Here's an
example:

Suppose we have:

    class Profile(models.Model):
        details = models.TextField()
        person = models.ForeignKey(Person)
    
        history = TrackChanges()

>>> philip = Person.objects.get(name='Philip')
>>> profile = Profile(details="Long walks on the beach", person=philip)
>>> profile.save()
# Now we change the description on the related model.
>>> philip.description = "Runs fast, writes code"
>>> philip.save()
# We get the most recent historical instance of the Profile object.
>>> profile_hist = profile.history.most_recent()
# This gives us a historical instance of the Person model at the
# correct point in time:
>>> profile_hist.person
<Person_hist: Person object as of 2011-02-15 20:33:03.409725>
>>> profile_hist.person.description
u'Some dude'
# The older description is displayed!  Yay!

This works similarly for ``OneToOneField`` and ``ManyToManyField``.

Reverse lookups do the right thing, too!  With a reverse lookup, 

***********************
here
***********************

Some more examples
------------------

Get all historical versions where the model was added, not just updated:

>>> from versionutils.versioning.constants import *
>>> Person.history.filter(history_info__type=TYPE_ADDED)
[<Person_hist: Person object as of 2011-02-15 21:53:15.613445>, <Person_hist: Person object as of 2011-02-15 17:23:20.483243>]

