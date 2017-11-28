from AccessControl import allow_type
from AccessControl.ZopeGuards import guarded_getattr
from AccessControl.ZopeGuards import guarded_getitem
from collections import Mapping

import pkg_resources
import string

try:
    # This hotfix does similar fixes, so it must be loaded first.
    # We want the new fix to be applied last.
    pkg_resources.get_distribution('Products.PloneHotfix20170117')
except pkg_resources.DistributionNotFound:
    pass
else:
    import Products.PloneHotfix20170117  # noqa
# And CMFPlone may have a safe_format.
try:
    from Products.CMFPlone import utils as plone_utils
except ImportError:
    # Be nice to a Zope or CMF instance without Plone
    plone_utils = None
# And AccessControl may have a safe_format.
try:
    from AccessControl import safe_formatter as access_safe_formatter
except ImportError:
    access_safe_formatter = None

try:
    # The Less config was introduced in Plone 5.
    # This should use the new SafeFormatter.
    from Products.CMFPlone.resources.browser import mixins
except ImportError:
    # Plone 3 or 4.
    mixins = None


class _MagicFormatMapping(Mapping):
    """
    Pulled from Jinja2

    This class implements a dummy wrapper to fix a bug in the Python
    standard library for string formatting.

    See http://bugs.python.org/issue13598 for information about why
    this is necessary.
    """

    def __init__(self, args, kwargs):
        self._args = args
        self._kwargs = kwargs
        self._last_index = 0

    def __getitem__(self, key):
        if key == '':
            idx = self._last_index
            self._last_index += 1
            try:
                return self._args[idx]
            except LookupError:
                pass
            key = str(idx)
        return self._kwargs[key]

    def __iter__(self):
        return iter(self._kwargs)

    def __len__(self):
        return len(self._kwargs)


class SafeFormatter(string.Formatter):

    def __init__(self, value):
        self.value = value
        super(SafeFormatter, self).__init__()

    def get_field(self, field_name, args, kwargs):
        """
        Here we're overridding so we can use guarded_getattr instead of
        regular getattr
        """
        first, rest = field_name._formatter_field_name_split()

        obj = self.get_value(first, args, kwargs)

        # loop through the rest of the field_name, doing
        #  getattr or getitem as needed
        for is_attr, i in rest:
            if is_attr:
                obj = guarded_getattr(obj, i)
            else:
                obj = guarded_getitem(obj, i)

        return obj, first

    def safe_format(self, *args, **kwargs):
        kwargs = _MagicFormatMapping(args, kwargs)
        return self.vformat(self.value, args, kwargs)


def safe_format(inst, method):
    """
    Use our SafeFormatter that uses guarded_getattr for attribute access
    """
    return SafeFormatter(inst).safe_format


# we want to allow all methods on string type except "format"
rules = dict([(m, True) for m in dir(str) if not m.startswith('_')])
rules['format'] = safe_format
allow_type(str, rules)

# Same for unicode instead of str.
rules = dict([(m, True) for m in dir(unicode) if not m.startswith('_')])
rules['format'] = safe_format
allow_type(unicode, rules)

if plone_utils is not None:
    # CMFPlone may already have the 20170117 hotfix merged
    # and then we need to override it with our better fix.
    # It can be there under two names.
    for name in ('_safe_format', 'safe_format'):
        if hasattr(plone_utils, name):
            setattr(plone_utils, name, safe_format)
    if hasattr(plone_utils, 'SafeFormatter'):
        plone_utils.SafeFormatter = SafeFormatter
if mixins is not None:
    if hasattr(mixins, 'SafeFormatter'):
        mixins.SafeFormatter = SafeFormatter
if access_safe_formatter is not None:
    # AccessControl may already have the 20170117 hotfix merged too.
    access_safe_formatter.safe_format = safe_format
