import os
import yaml

from .err import handle_error

SCRIPTDIRPATH = os.path.dirname(os.path.realpath(__file__))

_conf_obj = None

def get_kck_environment():
    return "dev" \
        if "KCK_ENVIRONMENT" not in os.environ \
            or os.environ["KCK_ENVIRONMENT"] not in ["dev", "prod", "test", "test-jwt", "test-refresh"] \
        else os.environ["KCK_ENVIRONMENT"]

def kck_config_lookup(*args, **kwargs):
    on_error = kwargs["on_error"] if "on_error" in kwargs else None
    conf_ptr = _get_config_object(on_error=on_error)

    if args is not None:
        for arg in args:
            conf_ptr = conf_ptr[arg]
    return conf_ptr

def _kck_config_filepath():
    if "KCK_CONFIG" in os.environ:
        return os.environ["KCK_CONFIG"]
    return os.path.join(SCRIPTDIRPATH, "..", "..", "config", "{}.yml".format(get_kck_environment()))

def _get_config_object(on_error=None):
    global _conf_obj
    if _conf_obj is None:
        with open(_kck_config_filepath(), 'r') as stream:
            try:
                _conf_obj = yaml.load(stream)
            except yaml.YAMLError as exc:
                handle_error(exc, "unable to init config object", on_error)
    return _conf_obj

