from json import JSONEncoder
from datetime import datetime, timezone


class JsonConverter(JSONEncoder):
    def default(self, o):
        print('Serializing type: {}'.format(type(o)))
        if isinstance(o, datetime) and o.tzinfo:
            return o.astimezone(timezone.utc).isoformat()
        return JSONEncoder.default(self, o)
