import json

class Policy(object):
    def __init__(self, version):
        self._policy = {'Version': version,
                        'Statement': []}

    @property
    def policy(self):
        return json.dumps(self._policy)

    def add_item(self, effect, actions, resources):
        raise NotImplementedError()

class IoTPolicy(Policy):
    def __init__(self, version='2012-10-17'):
        super().__init__(version)
    
    def add_item(self, effect, actions, resources):
        self._policy['Statement'].append({'Effect':effect,
                                          'Action':actions,
                                          'Resource':resources})