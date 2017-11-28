from Products.CMFPlone.URLTool import URLTool
from urlparse import urlparse
import pkg_resources

try:
    # This overrides isURLInPortal too, with earlier fixes, so it must be
    # loaded first.  This makes sure the import order is correct.
    pkg_resources.get_distribution('Products.PloneHotfix20160830')
except pkg_resources.DistributionNotFound:
    pass
else:
    import Products.PloneHotfix20160830  # noqa

try:
    # Python 2
    from HTMLParser import HTMLParser
except ImportError:
    # Python 3
    from html.parser import HTMLParser


hp = HTMLParser()
orig = URLTool.isURLInPortal


def wrapped_in_portal(self, url, context=None):
    schema, netloc, path, params, query, fragment = urlparse(url)
    if schema and schema not in ('http', 'https'):
        # Redirecting to 'data:' may be harmful,
        # and redirecting to 'mailto:' or 'ftp:' is silly.
        return False
    if path.endswith('&'):
        # This can happen in Python 2.4 when it gets confused.
        # This probably only happens for malicious urls.
        return False
    # Someone may be doing tricks with escaped html code.
    unescaped_url = hp.unescape(url)
    if unescaped_url != url:
        if not self.isURLInPortal(unescaped_url):
            return False
    try:
        return orig(self, url, context)
    except TypeError, e:
        if 'isURLInPortal() takes exactly 2 arguments' in e.args[0]:
            return orig(self, url)
        else:
            raise

wrapped_in_portal.__doc__ = orig.__doc__
URLTool.isURLInPortal = wrapped_in_portal
