import time

class CaptchaToken(object):
    def __init__(self, value, generation_time=time.time(), expiry_time=120):
        self.value = value
        self.generation_time = generation_time
        self.expiry_time = expiry_time

    def is_valid(self):
        return (time.time() - self.generation_time) < self.expiry_time
