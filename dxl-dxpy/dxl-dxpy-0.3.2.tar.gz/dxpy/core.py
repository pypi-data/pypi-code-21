""" base and core utilities of dxpy """
import json

class JSONSerializable:
    # @classmethod
    def to_json(self):
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, dct):
        return cls(**json.loads(dct))

def say_hello():
    print("Hello from dxpy.")