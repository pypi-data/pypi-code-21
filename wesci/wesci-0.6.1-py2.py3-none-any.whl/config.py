class Config(object):

    API_KEY = 'api_key'
    SECRET = 'secret'
    KEYS = set([API_KEY, SECRET])

    def load(self, conf_file_path):
        self.conf = {}

        with open(conf_file_path) as f:
            content = f.readlines()

        for line in content:
            self.conf.update(Config.process_conf_line(line))

        if not self.conf:   # old format conf
            self.conf[Config.API_KEY] = content[0].strip()

    def api_key(self):
        return self.conf[Config.API_KEY]

    def has_secret(self):
        return Config.SECRET in self.conf

    def secret(self):
        return self.conf[Config.SECRET]

    @staticmethod
    def process_conf_line(line):
        key = line.split('=')[0].strip()
        if key in Config.KEYS:
            return {key: line.split('=', 1)[1].strip()}
        return {}
