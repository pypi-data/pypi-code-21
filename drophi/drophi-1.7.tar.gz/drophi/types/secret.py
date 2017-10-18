import arrow
import base64

from .base import DockerObject

class Secret(DockerObject):
    "A docker swarm secret"
    def __init__(self, name, data=None, labels=None, id_=None, **kwargs):
        self.id_    = id_
        self.data   = data.encode('utf-8') if isinstance(data, str) else (data if data else b'no content')
        self.labels = labels or {}
        self.name   = name
        for k, v in kwargs.items():
            setattr(self, k, v)

    @staticmethod
    def parse(payload):
        return Secret(
            created_at  = arrow.get(payload['CreatedAt']),
            labels      = payload['Spec']['Labels'],
            id_         = payload['ID'],
            name        = payload['Spec']['Name'],
            updated_at  = arrow.get(payload['UpdatedAt']),
            version     = payload['Version']
        )

    def to_payload(self):
        return {
            'Name'      : self.name,
            'Data'      : base64.b64encode(self.data).decode('utf-8'),
            'Labels'    : self.labels,
        }

    async def create(self, client):
        payload = self.to_payload()
        results = await client.secret_create(payload)
        self.id_ = results['ID']
        return results

    async def delete(self, client):
        return await client.config_rm(self.id_)

class SecretMount(DockerObject):
    "A mount of a Secret inside of a Service"
    def __init__(self, secret, filename, mode=292, uid="0", gid="0"):
        self.filename   = filename
        self.gid        = gid
        self.mode       = mode
        self.secret     = secret
        self.uid        = uid

    def to_service_payload(self):
        return {
            'File'          : {
                'GID'       : self.gid,
                'Mode'      : self.mode,
                'Name'      : self.filename,
                'UID'       : self.uid,
            },
            'SecretID'      : self.secret.id_,
            'SecretName'    : self.secret.name,
        }

