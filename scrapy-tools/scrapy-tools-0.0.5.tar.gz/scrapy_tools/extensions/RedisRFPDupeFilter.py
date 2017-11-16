class RedisRFPDupeFilter():
    def request_seen(self, request):
        pass

    def request_fingerprint(self, request):
        pass

    def close(self, reason=''):
        pass

    def clear(self):
        pass

    def log(self, request, spider):
        pass