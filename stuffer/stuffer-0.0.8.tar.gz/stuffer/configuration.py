"""Application-wide configuration."""


class config(object):
    store_directory = None

    """Configuration parameters.

    Attributes
    ----------
    store_directory
        Directory where the key/value store is saved.  Can be overridden with the command line argument --store-dir.
    """
