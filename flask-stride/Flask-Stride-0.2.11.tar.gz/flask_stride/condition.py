from .module import Module

class ConditionClause(Module):
    clause_type = None

    def __init__(self, invert=None):
        if invert is not None:
            if not isinstance(invert, bool):
                raise ValueError('Unknown invert value: {}.'.format(invert))
            self.add_property('invert', invert)

class BuiltinConditionClause(ConditionClause):
    clause_type = 'built-in'
    valid_conditions = ['conversation_is_public', 'conversation_is_room']

    def __init__(self, condition, invert=None):
        super().__init__(invert=invert)
        if condition not in self.valid_conditions:
            raise ValueError('Unknown builtin condition: {}'.format(condition))

        self.add_property('condition', condition)

class CompositeConditionClause(ConditionClause):
    clause_type = 'composite'
    valid_types = ['or', 'OR', 'and', 'AND']

    def __init__(self, type, conditions, invert=None):
        super().__init__(invert=invert)

        # Validate the type parameter
        if type not in self.valid_types:
            raise ValueError('Unknown composite condition type: {}'.format(type))
        self.add_property('type', type.lower())

        # Validate the conditions parameter
        if isinstance(conditions, list) and len(conditions)<1:
            raise ValueError('Composite condition clause must have at least condition.')
        elif isinstance(conditions, ConditionClause):
            conditions = [ conditions ]
        elif isinstance(conditions, list):
            for c in conditions:
                if not isinstance(c, ConditionClause):
                    raise ValueError('Invalid condition clause: {}'.format(c))
        else:
            raise ValueError('Invalid condition type: {}.'.format(type(conditions)))
        self.add_property('conditions', conditions)
