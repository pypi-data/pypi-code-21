import logging
import pprint

import arrow

from .base import Port
from .config import ConfigMount
from .image import Image
from .network import Network
from .secret import SecretMount
from .volume import Mount

LOGGER = logging.getLogger(__name__)

class Endpoint():
    "The endpoint for a service"
    def __init__(self, ports, mode=None, virtual_ips=None):
        self.mode        = mode or 'vip'
        self.ports       = ports
        self.virtual_ips = virtual_ips

    def __eq__(self, other):
        return self.mode == other.mode and self.ports == other.ports

    @staticmethod
    def parse(payload):
        return Endpoint(
            ports       = [Port.parse(p) for p in payload.get('Ports', [])],
            mode        = payload.get('Spec', {}).get('Mode'),
            virtual_ips = payload.get('Spec', {}).get('VirtualIPs'),
        )

    def to_service_payload(self):
        return {
            'Mode'  : self.mode,
            'Ports' : [Port.to_service_payload(p) for p in self.ports],
        }

class NetworkAttachment():
    "An attachment of a service to a network"
    def __init__(self, network):
        self.network = network

    @staticmethod
    def parse(payload):
        return NetworkAttachment(network=Network(name=None, subnet=None, id_=payload['Target']))

    def to_service_payload(self):
        return {'Target': self.network.id_}

class Service():
    "A service in a docker swarm"
    def __init__(self, name, image, args=None, command=None, configs=None, constraints=None, data=None, endpoint=None, environment=None, id_=None, log_name=None, log_options=None, mode='replicated', mounts=None, networks=None, previous=None, replicas=1, secrets=None, version=None):
        self.args        = args or []
        self.command     = command
        self.configs     = configs or []
        self.constraints = constraints or []
        self.data        = data
        self.endpoint    = Endpoint.parse(endpoint) if isinstance(endpoint, str) else endpoint
        self.endpoint    = self.endpoint if self.endpoint else Endpoint([])
        self.environment = environment or {}
        self.id          = id_
        self.image       = Image.parse(image) if isinstance(image, str) else image
        self.log_name    = log_name
        self.log_options = log_options
        self.mode        = mode
        self.mounts      = mounts or []
        self.name        = name
        self.networks    = networks or []
        self.previous    = None
        self.replicas    = replicas
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
            'Mode'              : {},
            'Name'              : self.name,
            'TaskTemplate'      : {
                'ContainerSpec' : {
                    'Args'      : self.args,
                    'Command'   : self.command,
                    'Configs'   : [c.to_service_payload() for c in self.configs],
                    'Env'       : ["{}={}".format(k, v) for k, v in self.environment.items()],
                    'Image'     : self.image.to_payload(),
                    'Mounts'    : [m.to_service_payload() for m in self.mounts],
                },
                'Networks'          : [n.to_service_payload() for n in self.networks],
                'Placement'         : {
                    'Constraints'   : self.constraints,
                },
            },
        }
        # Lame, docker can't handle empty arrays properly :(
        if self.secrets:
            result['TaskTemplate']['ContainerSpec']['Secrets'] = [s.to_service_payload() for s in self.secrets]
        if self.log_name:
            result['TaskTemplate']['LogDriver'] = {
                'Name'  : self.log_name,
            }
        if self.log_options:
            result['TaskTemplate']['LogDriver']['Options'] = self.log_options
        if self.mode == 'replicated':
            result['Mode']['Replicated'] = {'Replicas' : self.replicas}
        return result

    @staticmethod
    def parse(payload):
        previous = payload.pop('PreviousSpec', None)
        LOGGER.debug("Parsing %s", pprint.pformat(payload))
        task = payload['Spec']['TaskTemplate']
        return Service(
            args        = task['ContainerSpec'].get('Args'),
            command     = task['ContainerSpec'].get('Command'),
            configs     = ConfigMount.parse(task['ContainerSpec'].get('Configs')),
            constraints = task.get('Placement', {}).get('Constraints'),
            data        = payload,
            endpoint    = Endpoint.parse(payload['Endpoint']),
            environment = _parse_environment(payload),
            name        = payload['Spec']['Name'],
            id_         = payload['ID'],
            image       = task['ContainerSpec']['Image'],
            log_name    = task.get('LogDriver', {}).get('Name'),
            log_options = task.get('LogDriver', {}).get('Options'),
            mode        = 'replicated' if 'Replicated' in payload['Spec']['Mode'] else 'global',
            mounts      = [Mount.parse(p) for p in payload['Spec']['TaskTemplate']['ContainerSpec'].get('Mounts', [])],
            networks    = [NetworkAttachment.parse(n) for n in task.get('Networks', [])],
            previous    = previous,
            replicas    = payload['Spec']['Mode'].get('Replicated', {}).get('Replicas'),
            secrets     = SecretMount.parse(task['ContainerSpec'].get('Secrets')),
            version     = payload['Version']['Index'],
        )

def _parse_environment(payload):
    env = payload['Spec']['TaskTemplate']['ContainerSpec'].get('Env', [])
    pairs = [item.partition('=') for item in env]
    pairs = [(item[0], item[2]) for item in pairs]
    return dict(pairs)
