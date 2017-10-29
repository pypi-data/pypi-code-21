
import types
from django.core.urlresolvers import reverse

def get_url(name, *args, **kwargs):
    return reverse(name, kwargs=kwargs, args=args)

def clean_dict(a, tr=None):
    """Removes any keys where the values is None"""
    for key in a.keys():
        if a[key] is None:
            a.pop(key)
        elif tr:
            a[key] = tr.get(unicode(a[key]), a[key])
    return a

def cached(f):
    """We save the details per request"""
    key = '_' + f.__name__
    def _call(self, *args, **kwargs):
        target = self.request
        field = key
        if args:
            field += '_' + ('_'.join(a for a in args if isinstance(a, basestring)))
        if not hasattr(target, field):
            ret = f(self, *args, **kwargs)
            if isinstance(ret, types.GeneratorType):
                ret = list(ret)
            setattr(target, field, ret)
        return getattr(target, field)
    return _call
