import logging
import pprint

import arrow

from .base import Port
from .image import Image
from .volume import Mount

LOGGER = logging.getLogger(__name__)

class Endpoint():
    "The endpoint for a service"
    def __init__(self, ports, mode='vip'):
        self.mode  = mode
        self.ports = ports

    def __eq__(self, other):
        return self.mode == other.mode and self.ports == other.ports

    @staticmethod
    def parse(payload):
        return Endpoint(
            ports = [Port.parse(p) for p in payload.get('Ports', [])],
        )

    def to_service_payload(self):
        return {
            'Mode'  : self.mode,
            'Ports' : [Port.to_service_payload(p) for p in self.ports],
        }

class Service():
    "A service in a docker swarm"
    def __init__(self, name, image, endpoint=None, id_=None, previous=None, version=None, command=None, configs=None, constraints=None, mounts=None, networks=None, secrets=None):
        self.command     = command
        self.configs     = configs or []
        self.constraints = constraints or []
        self.endpoint    = Endpoint.parse(endpoint) if isinstance(endpoint, str) else endpoint
        self.id          = id_
        self.image       = Image.parse(image) if isinstance(image, str) else image
        self.mounts      = mounts or []
        self.name        = name
        self.networks    = networks or []
        self.previous    = None
        self.secrets     = secrets or []
        self.version     = version

    def __eq__(self, other):
        if other is None:
            return False
        return all([getattr(self, prop) == getattr(other, prop) for prop in (
            'endpoint', 'image', 'mounts')])

    def __str__(self):
        return "Service {} {}".format(self.name, self.image)

    def __repr__(self):
        return str(self)

    async def create(self, client):
        payload = self.to_payload()
        return await client.service_create(payload)

    async def update(self, client):
        await client.service_update(
            self.old.id,
            self.old.version,
            payload,
        )

    def to_payload(self):
        result = {
            'EndpointSpec'      : self.endpoint.to_service_payload() if self.endpoint else None,
            'Name'              : self.name,
            'Networks'          : [n.to_service_payload() for n in self.networks],
            'TaskTemplate'      : {
                'ContainerSpec' : {
                    'Command'   : self.command,
                    'Configs'   : [c.to_service_payload() for c in self.configs],
                    'Image'     : self.image.to_payload(),
                    'Mounts'    : [m.to_service_payload() for m in self.mounts],
                },
                'Placement'         : {
                    'Constraints'   : self.constraints,
                },
            },
        }
        # Lame, docker can't handle empty arrays properly :(
        if self.secrets:
            result['TaskTemplate']['ContainerSpec']['Secrets'] = [s.to_service_payload() for s in self.secrets]
        return result

    @staticmethod
    def parse(payload):
        previous = payload.pop('PreviousSpec', None)
        LOGGER.debug("Parsing %s", pprint.pformat(payload))
        return Service(
            endpoint = Endpoint.parse(payload['Endpoint']),
            name     = payload['Spec']['Name'],
            id_      = payload['ID'],
            image    = payload['Spec']['TaskTemplate']['ContainerSpec']['Image'],
            mounts   = [Mount.parse(p) for p in payload['Spec']['TaskTemplate']['ContainerSpec'].get('Mounts', [])],
            networks = [Network.parse(n) for n in payload.get('Networks', [])],
            previous = previous,
            version  = payload['Version']['Index'],
        )

