from xstatic.main import XStatic

from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def xstatic(modname, filename):
    try:
        # list of tuples of the form (cdnname, protocol)
        cdns = settings.CDNS
    except AttributeError:
        cdns = []
    if settings.DEBUG:
        filename = filename.replace('.min.', '.')

    if cdns:
        modname = str(modname.replace('-', '_'))
        pkg = __import__('xstatic.pkg', fromlist=[modname])
        mod = getattr(pkg, modname)
        for cdnname, protocol in cdns:
            try:
                base_url = XStatic(mod, provider=cdnname, protocol=protocol).base_url
            except KeyError:
                continue
            if isinstance(base_url, str):
                # base_url is often a str
                return base_url + '/' + filename
            else:
                # But it also can be a dict (which maps relative paths to
                # full urls) (this happens with jquery CDN)
                if filename in base_url:
                    return base_url.get(filename)

    return settings.STATIC_URL + 'xstatic/' + filename
