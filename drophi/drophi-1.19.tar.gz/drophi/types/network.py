from .base import DockerObject

class Network(DockerObject):
    "A docker network"
    def __init__(self, name, subnet, driver='bridge', id_=None):
        self.driver   = driver
        self.id_      = id_
        self.name     = name
        self.subnet   = subnet

    @staticmethod
    def parse(payload):
        return Network(
            id_         = payload['Id'],
            name        = payload['Name'],
            subnet      = payload['IPAM']['Config'][0]['Subnet'] if payload['IPAM']['Config'] else None,
        )

    def to_payload(self):
        return {
            'Name'              : self.name,
            'CheckDuplicate'    : True,
            'Driver'            : self.driver,
            'IPAM'              : {
                'Driver'        : 'default',
                'Config'        : [{
                    'Subnet'    : self.subnet,
                }],
            },
        }

    def to_service_payload(self):
        return {
            'Target'      : self.id_ or self.name,
        }

    async def create(self, client):
        payload = self.to_payload()
        results = await client.network_create(payload)
        self.id_ = results['Id']
        return results
