"""
General constants
"""
from colorama import Back
from colorama import Fore
from colorama import Style

from mhelper import file_helper

__author__ = "Martin Rusilowicz"




# Root names
# - Names of items in the $(APP_DISPLAY_NAME) root object (in the object explorer)
EXPLORER_KEY_LAST_RESULT = "Results"
EXPLORER_KEY_PLUGINS     = "Plugins"
EXPLORER_KEY_DOCKETS     = "Saved_Results"
ENDPOINT_TYPE = "ENDPOINT"

KEYRING_NAME = "neocommand"

# Plugin types
PLUGIN_TYPE_SCRIPT  = "Script"
PLUGIN_TYPE_COMMAND = "Command"
PLUGIN_TYPE_MODULE  = "Module"
PLUGIN_TYPE_PARSER  = "Parser"


# Application information
APP_DISPLAY_NAME        = "NeoCommand"
APP_ABBREVIATED_NAME    = "neocommand"
APP_CONSOLE_NAME        = "{} CONSOLE INTERACTIVE SHELL"  # Display title of the console
APP_PY_INTERACTIVE_NAME = "{} PYTHON INTERACTIVE SHELL"   # Display title of the Python interactive shell
APP_PY_INTERFACE_NAME   = "{} PYTHON SCRIPTING INTERFACE" # Display title of the Python interactive shell
APP_GUI_NAME            = "{} QT GRAPHICAL INTERFACE"     # Display title of the GUI

# CLI prompts
PROMPT_QUESTION      = "QUERY>"
PROMPT               = APP_ABBREVIATED_NAME.upper() + ">"


# Filenames
FILENAME_CYPHER      = "import.cypher"
FILENAME_SHELL       = "import.sh"
FILENAME_NODE_PREFIX = "node"
FILENAME_EDGE_PREFIX = "edge"

# Folders
FOLDER_PIPELINES         = "user_endpoints"
FOLDER_DOCKETS           = "dockets"

# Extensions
# - Defining the following might seem strange,
#   but if we don't Lint tries to reinterpret strings in annotations as type-names and throws errors
#   Putting the strings in real values fixes this
EXT_B42CSV = ".typed_csv"
EXT_B42ZIP = ".parcel_zip"
EXT_CYPHER = ".cypher"
EXT_TXT    = ".txt"
EXT_SH     = ".sh"
EXT_CSV    = ".csv"
EXT_GEXF   = ".gexf"
EXT_NPZ    = ".npz"
EXT_NONE   = ""
EXT_LOCAL_DATA = ".local_data"

# Node labels 
PROP_ALL_PRIMARY_KEY   = "uid"

# Neo4j special strings
NEO4J_START_ID_TYPE         = "START_ID"
NEO4J_END_ID_TYPE           = "END_ID"
NEO4J_ID_TYPE               = "ID"
NEO4J_START_ID_SUFFIX       = ":" + NEO4J_START_ID_TYPE
NEO4J_END_ID_SUFFIX         = ":" + NEO4J_END_ID_TYPE
NEO4J_ID_SUFFIX             = ":" + NEO4J_ID_TYPE
PRIMARY_KEY_DECORATED_NAME  = PROP_ALL_PRIMARY_KEY + NEO4J_ID_SUFFIX


PREFIX_UNIX                 = "file:///"
PREFIX_WINDOWS              = "file:/"
KEYWORD_MERGE               = "MERGE"
KEYWORD_CREATE              = "CREATE"


# Times
TIME_FIVE_MIN       = 60 * 5
TIME_ONE_MIN        = 60
TIME_ONE_HOUR       = 60 * 60
TIME_SHORT_TIMEOUT  = TIME_ONE_MIN * 5
TIME_MEDIUM_TIMEOUT = TIME_ONE_HOUR * 5

# Default script parameters
DEFAULT_DELETE_LIMIT = 1000



COL_CRIT = Back.RED + Fore.WHITE  # error
COL_INFO = Back.WHITE + Fore.BLUE
COL_ERR = Fore.RED  # error
COL_TITLE = Back.BLACK + Style.BRIGHT + Fore.GREEN  # titles
COL_WARN = Back.YELLOW + Fore.BLACK
COL_ARG = Fore.CYAN  # arguments
COL_KEY = Fore.GREEN
COL_VAL = Fore.CYAN
COL_ITEM = Fore.GREEN
COL_CMD = Fore.GREEN  # commands

if file_helper.is_windows():
    LIGHT_BG = Back.BLACK
else:
    LIGHT_BG = Back.LIGHTBLACK_EX

COLX = Style.RESET_ALL  # nothing