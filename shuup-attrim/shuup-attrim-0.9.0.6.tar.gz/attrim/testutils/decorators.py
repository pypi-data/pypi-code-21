from shuup_utils.settings import LANG_CODES


def require_enabled_languages(*required_languages):
    """
    Throw an error if site setting doesn't contain required languages.
    """
    # noinspection PyShadowingBuiltins
    def real_decorator(function):
        for required_lang in required_languages:
            if required_lang not in LANG_CODES:
                raise AttributeError(
                    'Site does not have language required for this test.'
                )
        return function
    return real_decorator
