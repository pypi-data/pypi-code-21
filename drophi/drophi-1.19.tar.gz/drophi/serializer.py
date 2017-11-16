import logging
import pprint

import drophi.types

LOGGER = logging.getLogger(__name__)

class Serializer():
    pass

class Mount(Serializer):
    @staticmethod
    def from_payload(payload):
        return drophi.types.Mount(
            source  = payload.get('Source'),
            target  = payload.get('Target'),
            type    = payload['Type'],
        )

    @staticmethod
    def to_payload(mount):
        return {
            'Source'    : mount.source.name,
            'Target'    : mount.target,
            'Type'      : mount.type,
        }
