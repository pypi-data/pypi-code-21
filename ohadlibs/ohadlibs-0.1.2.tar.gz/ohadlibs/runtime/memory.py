import json


class Memory:

    def __init__(self):
        self.path = "runtime_data.json"
        self.data = {}

    def set(self, key, value):
        self.data[key] = value
        self.save()
        return

    def get(self, key):
        return self.data.get(key)

    def restore(self):
        return json.loads(open(self.path, 'r').read())

    def save(self):
        f = open(self.path, 'w')
        f.write(json.dumps(self.data))
        f.close()
        return

    def clear(self):
        f = open(self.path, 'w')
        f.close()
