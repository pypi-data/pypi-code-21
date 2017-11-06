import consul
from consul_lock import EphemeralLock


class Lock(object):
    def __init__(self, key, timeout=60):
        self.key = key
        self.client = consul.Consul()
        self.lock = EphemeralLock(key, consul_client=self.client, acquire_timeout_ms=timeout * 1000)

    def acquire(self, fail_hard=False):
        return self.lock.acquire(fail_hard)

    @property
    def version(self):
        (idx, value) = self.client.kv.get(self.key)
        if value and value['Value']:
            return int(value['Value'])
        return -1

    @version.setter
    def version(self, value):
        self.client.kv.put(self.key, value)

    def release(self):
        return self.lock.release()
