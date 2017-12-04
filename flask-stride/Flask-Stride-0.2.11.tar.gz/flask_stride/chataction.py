from .module import Module
from .condition import BuiltinConditionClause, CompositeConditionClause

class ChatAction(Module):

    def __init__(self, key, name, target, weight=None, conditions=None):
        super().__init__(key)
        self.add_property('name', {'value': name})
        self.add_property('target', target)
        if weight is not None:
            self.add_property('weight', weight)
        if conditions is not None:
            self.add_property('conditions', conditions)
