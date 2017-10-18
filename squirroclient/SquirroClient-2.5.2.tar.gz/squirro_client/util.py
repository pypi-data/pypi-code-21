import warnings


def deprecation(message):
    warnings.warn(message, DeprecationWarning, stacklevel=2)

# Enable deprecation warnings.
warnings.simplefilter("default")
