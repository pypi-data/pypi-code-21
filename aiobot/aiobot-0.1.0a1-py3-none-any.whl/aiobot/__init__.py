# Authors: Josh Bourquin

# Package version information, these values should be updated as development progresses
__version_number__ = (0, 1, 0)  # Ex: 0.1.0, should conform to semantic versioning 2.0.0
__version_tag__ = 'a1'		# Ex: a1, b1, rc1; Remove for stable versions

# Auto generated version and relase info, do not modify
__version__ = '.'.join(str(n) for n in __version_number__)
if __version_tag__:
    __version__ = '{}{}'.format(__version__, __version_tag__)