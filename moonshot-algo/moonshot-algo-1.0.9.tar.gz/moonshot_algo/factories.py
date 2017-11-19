from entities import Config
from models import Model, SimpleModel

__MODEL_DICTIONARY = {
    "simple": lambda config: SimpleModel(config)
}


def __extract_name_from_config(config):
    """

    :param Config config:
    :return: the name of the model
    """
    return config.modelConfig.name


def create_model(config):
    """

    :param Config config:
    :return: the model
    :rtype: Model
    """
    name = __extract_name_from_config(config)
    if name in __MODEL_DICTIONARY:
        return __MODEL_DICTIONARY[name](config)
    else:
        raise ValueError("no such model")
