class NotDictError(TypeError):
    def __init__(self, true_type):
        super(__class__, self).__init__(
            "Need dict type, got {}.".format(true_type)
        )

class NotTreeDictError(TypeError):
    def __init__(self, true_type):
        super(__class__, self).__init__(
            "Need TreeDict type, got {}.".format(true_type)
        )


class KeyNotDictError(TypeError):
    def __init__(self, name, true_type):
        super(__class__, self).__init__(
            "Key {name} is supposed to be a dict, got {true_type}".format(name=name, true_type=true_type))
