===============================================
``versionutils.versioning``
===============================================

The ``versioning`` app is a smart and flexible versioning system for models.  Existing model versioning systems left much to be desired.  Major advantages over existing versioning systems are:

* Super-sexy ORM access to historical model data.
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

Ready to get started?  Great!  Just read below:

.. toctree::
   :maxdepth: 2

   install
   usage
   reference
   notes
   extend
   contribute
