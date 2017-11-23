import appdirs
import os
from .utils import load_conf


DEFAULT_LOCAL_DATA_DIR = appdirs.user_data_dir("modelhub")
LOCAL_DATA_DIR = DEFAULT_LOCAL_DATA_DIR
LOCAL_MODEL_DIR = os.path.join(LOCAL_DATA_DIR, "models")

RC_PATH = "~/.modelhubrc"

USER_NAME = None
USER_EMAIL = None

from modelhub.settings import *   # noqa

RC_PATH = os.path.expanduser(RC_PATH)
if os.path.exists(RC_PATH):
    load_conf(RC_PATH, locals())
