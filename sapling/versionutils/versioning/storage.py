"""
  * Right now we simply block delete() on FileFields.  Django's default
    behavior is to never override a file -- it simply renames it
    whatever_2.txt. This will work for us, for now.

      * This will work for our (localwiki) purposes because we'll probably
        have a separate model for the actual file and we can have a long
        name attribute on it to mask the lame_name_45.jpg from the end user.

  * MAYBE: We may want to create a custom storage system that does other nice
    things like creates magic nested directories to hold files to avoid
    having 400,000 files in a single directory.  So when we deal with
    this we can look at doing fancy things.
"""


class FileStorageWrapper(object):
    """
    Prevents file deletion.

    Django doesn't automatically delete files from FileFields when a model's
    delete() method is called.  But Django will delete the file on disk when
    the FileField's delete() method is called directly.
    """
    def __init__(self, storage):
        self._storage = storage

    def __getattr__(self, label):
        return getattr(self._storage, label)

    def delete(self, label):
        pass
