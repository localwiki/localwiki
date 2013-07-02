from django.contrib.auth.hashers import *


# Copied from Django 1.5 - TODO: remove once we're on 1.5
# This hasher is required for porting over some very old sites.

class UnsaltedSHA1PasswordHasher(BasePasswordHasher):
    """
    Very insecure algorithm that you should *never* use; stores SHA1 hashes
    with an empty salt.

    This class is implemented because Django used to accept such password
    hashes. Some older Django installs still have these values lingering
    around so we need to handle and upgrade them properly.
    """
    algorithm = "unsalted_sha1"

    def salt(self):
        return ''

    def encode(self, password, salt):
        assert salt == ''
        hash = hashlib.sha1(force_bytes(password)).hexdigest()
        return 'sha1$$%s' % hash

    def verify(self, password, encoded):
        encoded_2 = self.encode(password, '')
        return constant_time_compare(encoded, encoded_2)

    def safe_summary(self, encoded):
        assert encoded.startswith('sha1$$')
        hash = encoded[6:]
        return SortedDict([
            (_('algorithm'), self.algorithm),
            (_('hash'), mask_hash(hash)),
        ])
