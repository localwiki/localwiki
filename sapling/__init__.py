VERSION = (0, 2, 'beta', 15)


def get_version():
    version = '%s.%s' % (VERSION[0], VERSION[1])
    if VERSION[2:] == ('alpha', 0):
        version = '%s pre-alpha' % version
    else:
        if VERSION[2] != 'final':
            version = '%s %s %s' % (version, VERSION[2], VERSION[3])
    return version
