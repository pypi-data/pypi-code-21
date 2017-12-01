

class ProcessingRules(object):
    def __init__(self):
        self.rules = {}

    def add(self, method_name, user_implementation, client_action):
        self.rules[method_name] = ProcessingRule(user_implementation, client_action)

    def on(self, method_name):
        return ProcessingRuleBuilder(self, method_name)


class ProcessingRule(object):
    def __init__(self, user_implementation, client_action):
        self.user_implementation = user_implementation
        self.client_action = client_action


class ProcessingRuleBuilder(object):
    def __init__(self, instance, method_name):
        self.instance = instance
        self.method_name = method_name
        
    def call(self, user_implementation):
        self.user_implementation = user_implementation
        return self

    def then(self, client_action):
        self.instance.add(self.method_name, self.user_implementation, client_action)
