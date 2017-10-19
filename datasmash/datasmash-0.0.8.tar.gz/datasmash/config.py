import os
import uuid


TEMP_DIR = str(uuid.uuid4()).replace("-","")
TEMP_DIR = TEMP_DIR.replace("-", "")
PREFIX = str(uuid.uuid4())
CWD = os.getcwd()
BIN_PATH = os.path.dirname(os.path.realpath(__file__)) + '/bin/'

