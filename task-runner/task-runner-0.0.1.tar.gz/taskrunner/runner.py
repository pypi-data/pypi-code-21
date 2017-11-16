import traceback
import time

class TaskRunner(object):
    def __init__(self, logger=None):
        self.logger = logger

    def run_until_complete(self, target=None, args=(), interval=0.01, exclude=[]):
        returned = False
        while not returned:
            try:
                result = target(*args)
                if result not in exclude:
                    returned = True
            except Exception:
                error = traceback.format_exc()
                if self.logger:
                    self.logger.error(error)
            time.sleep(interval) # Avoid busy waiting
        return result
