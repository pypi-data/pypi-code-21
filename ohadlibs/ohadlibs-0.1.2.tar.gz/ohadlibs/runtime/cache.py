import json
import os
import time

from ohadlibs.runtime.logger.log import Log

class Cache:

    def __init__(self, **kwargs):
        self.dir = 'cache'
        if not os.path.exists(self.dir):
            os.mkdir(self.dir)
        self.name = kwargs['name'] if 'name' in kwargs else 'data'
        self.path = os.path.join(self.dir, "{}.json".format(self.name))
        self.logger = Log('cache', os.path.join(self.dir, 'logs'))
        self.last_update_log_path = os.path.join(self.dir, 'last_update.log')
        self.max_seconds_between_caches = 3600  # 1 Hour
    
    def set_max_seconds_between_caches(self, max_seconds_between_caches):
        self.max_seconds_between_caches = max_seconds_between_caches
    
    def get_last_update_time(self):
        return float(open(self.last_update_log_path, 'r').read())

    def set_last_update_time(self):
        f = open(self.last_update_log_path, 'w')
        curr_time = time.time()
        f.write(str(curr_time))
        return curr_time

    def is_up_to_date(self):
        if not os.path.exists(self.last_update_log_path):
            open(self.last_update_log_path, 'w').write('0')
            return False
        return time.time() - self.get_last_update_time() < 3600

    def cache(self, json_data):
        json_file = open(self.path, 'w')
        json_file.write(json_data)
        self.set_last_update_time()

    def restore(self):
        return json.loads(open(self.path, 'r').read())
