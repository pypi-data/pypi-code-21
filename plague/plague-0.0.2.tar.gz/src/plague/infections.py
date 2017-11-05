from base64 import b64encode, b64decode

import json
import pickle


class InfectionEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (list, dict, str, int, float, bool, type(None))):
            return super().default(obj)
        return {'_set': b64encode(pickle.dumps(obj)).decode('utf-8')}


def infection_decoder(data):
    if '_set' in data:
        return pickle.loads(b64decode(data['_set'].encode('utf-8')))
    return data


class Infection:
    def __init__(self, host, port, message, susceptible_nodes=None, infected_nodes=None):
        """
        The ``Infection`` object is effectively a message container.
        Plague delegates managing who has ack'd a message using this object.

        """
        self.host = host
        self.port = port
        self.message = message

        # establish infected nodes
        self.infected_nodes = set(infected_nodes) if infected_nodes else set()

        # initialize an infection with the sender's list of susceptible nodes
        # and include the sender so the infection goes full circle
        self.susceptible_nodes = set(susceptible_nodes) if susceptible_nodes else set()
        self.susceptible_nodes.add((self.host, self.port))

    @classmethod
    def from_bytes(cls, bytes_):
        data = json.loads(str(bytes_.decode('utf8')), object_hook=infection_decoder)
        return cls(**data)

    def __bytes__(self):
        """ We call ``bytes`` to pickle ourself """
        return bytes(json.dumps(self.__dict__, cls=InfectionEncoder).encode('utf8'))
