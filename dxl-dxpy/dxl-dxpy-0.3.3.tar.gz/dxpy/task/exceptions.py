from .database import TaskNotFoundError, TaskDatabaseConnectionError, InvalidJSONForTask


class ServiceNotFound(Exception):
    def __init__(self, name):
        super(__class__, self).__init__(
            "{name} service not found.".format(name=name))


class UnknownConfigName(Exception):
    def __init__(self, name):
        super(__class__, self).__init__(
            "Unknown config name: {name}.".format(name=name))


class UnknownTemplateNameError(Exception):
    def __init__(self, ukn_name):
        super(__class__, self).__init__("Unknown task template name {name}, suppoted names are {supp}.".format(
            name=ukn_name, supp=[k for k in TEMPLATE_NAME_MAP.keys()]))
