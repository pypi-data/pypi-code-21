# -*- coding: utf-8 -*-
import json
import logging

from jsonpublish import dumps
from jsonpublish import jsonsettings
from datetime import datetime

from pytz import timezone
import hashlib

log = logging.getLogger(__name__)


def _action_from_request(request):
    if request.method == 'POST':
        return 'aanmaken'
    elif request.method == 'PUT':
        return 'bewerken'
    elif request.method == 'DELETE':
        return 'verwijderen'
    elif request.method == 'GET':
        return 'opvragen'
    else:
        return 'onbekend'


def _get_versie_hash(wijziging):
    timestamp = datetime.now(tz=timezone('CET'))
    inputversie = "{0}{1}{2}".format(timestamp, wijziging.resource_object_id, wijziging.updated_by)
    versie = hashlib.sha256(bytearray(inputversie, "utf-8")).hexdigest()
    return versie


def audit(**kwargs):
    """
    use this decorator to audit an operation
    """

    def wrap(fn):

        def advice(parent_object, *args, **kw):
            request = parent_object.request
            wijziging = request.audit_manager.create_revision()

            result = fn(parent_object, *args, **kw)

            if hasattr(request, 'user') and request.user is not None and 'actor' in request.user:
                actor = request.user['actor']
                wijziging.updated_by = actor.get('uri', None)
                wijziging.updated_by_omschrijving = actor.get('omschrijving', None)
            else:
                wijziging.updated_by = 'publiek'
                wijziging.updated_by_omschrijving = 'publiek'

            r_id = request.matchdict.get('id')
            wijziging.resource_object_id = r_id
            if result is not None:
                wijziging.resource_object_id = result.id if not r_id else int(r_id)
                try:
                    wijziging.resource_object_json = json.loads(dumps(jsonsettings(result, request=request)))
                except Exception as e:
                    log.error(e)

            wijziging.versie = _get_versie_hash(wijziging)
            wijziging.actie = kwargs.get('actie') if kwargs.get('actie') else _action_from_request(request)

            request.audit_manager.save(wijziging)

            return result

        return advice

    return wrap
