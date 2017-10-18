from .base import DockerObject

class Mount(DockerObject):
    PROPERTIES = ('readonly', 'source', 'target', 'type')
    def __init__(self, source, target, type='volume', readonly=True):
        self.readonly   = readonly
        self.source     = source
        self.target     = target
        self.type       = type

    def __eq__(self, other):
        return all([getattr(self, p) == getattr(other, p) for p in (
            'readonly', 'source', 'target', 'type')])

    def to_container_payload(self):
        return '{source}:{target}:{flag}'.format(
            source  = self.source,
            target  = self.target,
            flag    = 'ro' if self.readonly else 'rw',
        )

    def to_service_payload(self):
        return {
            'Target'        : self.target,
            'Source'        : self.source.name if isinstance(self.source, Volume) else self.source,
            'Type'          : self.type,
            'ReadOnly'      : self.readonly,
            'Consistency'   : 'default',
        }

    @classmethod
    def parse(cls, payload):
        return cls(
            readonly = payload.get('ReadOnly', True),
            source   = payload['Source'],
            target   = payload['Target'],
            type     = payload['Type'],
        )

class Volume(DockerObject):
    PROPERTIES = ('driver', 'labels', 'mountpoint', 'name', 'options', 'scope')
    def __init__(self, name, driver='local', labels=None, mountpoint=None, options=None, scope='local'):
        self.driver     = driver
        self.labels     = labels or {}
        self.mountpoint = mountpoint
        self.options    = options or {}
        self.name       = name
        self.scope      = scope

    def __str__(self):
        return f'Volume {self.name}'

    async def create(self, client):
        payload = self.to_payload()
        return await client.volume_create(payload)

    async def delete(self, client):
        return await client.volume_rm(self.name)

    @classmethod
    def parse(cls, payload):
        return cls(
            driver      = payload['Driver'],
            labels      = payload['Labels'] or {},
            mountpoint  = payload['Mountpoint'],
            name        = payload['Name'],
            options     = payload['Options'],
            scope       = payload['Scope'],
        )

    def to_payload(self):
        return {
            'Name'          : self.name,
            'Driver'        : 'local',
            'DriverOpts'    : {},
            'Labels'        : self.labels,
        }
