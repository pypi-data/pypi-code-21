import hashlib

from django.core.exceptions import FieldDoesNotExist
try:
    from django.urls import reverse
except ImportError:  # Django<2.0
    from django.core.urlresolvers import reverse
from django.db import models
from django.http import QueryDict


def get_object_ids(request, objects):
    selected = [str(o.pk) for o in objects]
    session = request.session
    object_ids = ",".join(selected)
    if len(object_ids) > 500:
        hash_id = "session-%s" % \
            hashlib.md5(object_ids.encode('utf-8')).hexdigest()
        session[hash_id] = object_ids
        session.save()
        object_ids = hash_id
    return object_ids


def build_redirect_url(request, *args, **kwargs):
    params = kwargs.pop('params', {})
    url = reverse(*args, **kwargs)
    if not params:
        return url

    qdict = QueryDict('', mutable=True)
    for k, v in params.items():
        qdict[k] = get_object_ids(request, v)

    return url + '?' + qdict.urlencode()


class LargeInitialMixin(object):
    def get_changeform_initial_data(self, request):
        """
        Get the initial form data.
        Unless overridden, this populates from the GET params.
        """
        initial = dict(request.GET.items())
        for k in initial:
            try:
                f = self.model._meta.get_field(k)
            except FieldDoesNotExist:
                continue
            # We have to special-case M2Ms as a list of comma-separated PKs.
            if isinstance(f, models.ManyToManyField):
                if initial[k].startswith("session-"):
                    initial[k] = request.session.get(initial[k]).split(",")
                else:
                    initial[k] = initial[k].split(",")
        return initial
