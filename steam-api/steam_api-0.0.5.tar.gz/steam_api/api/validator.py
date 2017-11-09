from .language_code import LANGUAGE_CODE
from ..error import ParameterNotInEnumError


def check_language(original_function):
    """
    check language code
    :param original_function:
    :return:
    """
    def new_function(*args, **kwargs):
        for name, value in kwargs.items():
            if name == 'language' and value not in LANGUAGE_CODE.keys():
                raise ParameterNotInEnumError('language %s not supported' % value)

        return original_function(*args, **kwargs)

    return new_function
