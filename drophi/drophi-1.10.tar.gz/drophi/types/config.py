import arrow
import base64

from .base import DockerObject

class Config(DockerObject):
    "A docker swarm config"
    def __init__(self, name, data, labels=None, id_=None, **kwargs):
        self.id_    = id_
        self.data   = data.encode('utf-8') if isinstance(data, str) else data
        self.labels = labels or {}
        self.name   = name
        for k, v in kwargs.items():
            setattr(self, k, v)

    @staticmethod
    def parse(payload):
        return Config(
            created_at  = arrow.get(payload['CreatedAt']),
            data        = base64.b64decode(payload['Spec']['Data']),
            labels      = payload['Spec']['Labels'],
            id_         = payload['ID'],
            name        = payload['Spec']['Name'],
            updated_at  = arrow.get(payload['UpdatedAt']),
            version     = payload['Version']
        )

    def to_payload(self):
        return {
            'Data'      : base64.b64encode(self.data).decode('utf-8'),
            'Labels'    : self.labels,
            'Name'      : self.name,
        }

    def to_service_payload(self):
        raise Exception("looks like you're trying to specify a Config directly in a service. Use a ConfigMount instead")

    async def create(self, client):
        payload = self.to_payload()
        results = await client.config_create(payload)
        self.id_ = results['ID']
        return results

    async def delete(self, client):
        return await client.config_rm(self.id_)

class ConfigMount(DockerObject):
    "A mount of a Config inside of a Service"
    def __init__(self, config, filename, mode=292, uid="0", gid="0"):
        self.config     = config
        self.gid        = gid
        self.filename   = filename
        self.mode       = mode
        self.uid        = uid

    def to_service_payload(self):
        return {
            'File'          : {
                'Name'      : self.filename,
                'GID'       : self.gid,
                'Mode'      : self.mode,
                'UID'       : self.uid,
            },
            'ConfigID'      : self.config.id_,
            'ConfigName'      : self.config.name,
        }

