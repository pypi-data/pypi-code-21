from mhelper import ansi as __A__


_RESET__                             = "\033[0m"

#
# Special
#
RESET                                = _RESET__                                         # Normal text

# Titles
TITLE                                = _RESET__ + __A__.BACK_BLUE + __A__.FORE_WHITE                # Titles (heading 1)
HEADING                              = _RESET__ + __A__.FORE_MAGENTA                          # Headings (heading 2)

# General
EMPHASIS                             = _RESET__ + __A__.FORE_BLUE                             # Quotes
EMPHASIS_EXTRA                       = _RESET__ + __A__.FORE_BRIGHT_WHITE + __A__.BACK_LIGHT_BLACK                            # Quotes
COMMENT                              = _RESET__ + __A__.DIM                             # Comments, descriptions
BOLD                                 = _RESET__ + __A__.FORE_YELLOW                           # Key points
BOLD_EXTRA                           = _RESET__ + __A__.FORE_YELLOW + __A__.BACK_BLUE               # Key points, including spaces

# Unique
ENUMERATION                          = _RESET__ + __A__.FORE_MAGENTA                          # Enumerations, options
FIELD_NAME                           = _RESET__ + __A__.FORE_YELLOW                           # Field names
ARGUMENT_NAME                        = _RESET__ + __A__.FORE_CYAN                             # Argument names
VALUE                                = _RESET__ + __A__.FORE_YELLOW                           # Argument values
COMMAND_NAME                         = _RESET__ + __A__.FORE_GREEN                            # Command names, variable names
COMMAND_NAME_BOLD                    = _RESET__ + __A__.FORE_BRIGHT_GREEN                               # Emphasised form of COMMAND_NAME
CORE_NAME                            = _RESET__ + __A__.FORE_YELLOW                           # Emphasised form of COMMAND_NAME
SYSTEM_NAME                          = _RESET__ + __A__.FORE_RED                              # Emphasised form of COMMAND_NAME

# Status
STATUS_NO                            = _RESET__ + __A__.FORE_RED                              # No settings
STATUS_YES                           = _RESET__ + __A__.FORE_GREEN                            # Yes settings
STATUS_INTERMEDIATE                  = _RESET__ + __A__.FORE_CYAN                             # Intermediate, neither, settings
STATUS_IS_SET                        = _RESET__ + __A__.BACK_BLUE                             # Unset settings
STATUS_IS_NOT_SET                    = _RESET__                                         # Set settings

# Boxes
BORDER                               = _RESET__ + __A__.FORE_BRIGHT_BLACK + __A__.DIM        # Borders and lines, deemphasised
BOX_TITLE                            = _RESET__ + __A__.FORE_BRIGHT_WHITE + __A__.BOLD     # Titles inside tables
BOX_TITLE_RIGHT                      = _RESET__ + __A__.BACK_CYAN + __A__.FORE_BLACK                # Titles inside titles

# Internal streams
WARNING                              = _RESET__ + __A__.BACK_YELLOW + __A__.FORE_RED                # Warnings
ERROR                                = _RESET__ + __A__.FORE_RED                              # Errors
PROMPT                               = _RESET__ + __A__.FORE_YELLOW                           # Prompts

# IO Streams
IO_COMMAND                           = _RESET__ + __A__.FORE_CYAN                             # Streams to command line
IO_STDOUT                            = _RESET__ + __A__.FORE_GREEN                            # Streams from command line
IO_STDERR                            = _RESET__ + __A__.FORE_RED                              # Streams from command line

# Console explorer box
CX_BORDER                            = _RESET__ + __A__.FORE_BLUE
CX_HEADING                           = _RESET__ + __A__.BACK_BLUE + __A__.FORE_WHITE
CX_VALUE                             = _RESET__ + __A__.DIM
CX_CLASS                             = _RESET__ + __A__.FORE_BRIGHT_BLACK
CX_SPACER_1                          = _RESET__ + __A__.FORE_BRIGHT_BLACK + __A__.DIM
CX_SPACER_2                          = _RESET__ + __A__.FORE_YELLOW + __A__.DIM

# Startup banner
BANNER_ZERO                          = _RESET__ + __A__.FORE_BLUE + __A__.BACK_BLUE
BANNER_MAIN                          = _RESET__ + __A__.FORE_BLUE + __A__.BACK_YELLOW
BANNER_REVERSED                      = _RESET__ + __A__.FORE_YELLOW + __A__.BACK_BLUE
BANNER_END_OF_THE_LINE               = _RESET__ + __A__.FORE_BLUE 
BANNER_COMMAND_NAME                  = _RESET__ + __A__.FORE_RED + __A__.BACK_YELLOW

# Query
QUERY_PREFIX                         = _RESET__ + __A__.FORE_WHITE + __A__.BACK_BLUE
QUERY_MESSAGE                        = _RESET__ + __A__.FORE_MAGENTA
QUERY_OPTION                         = _RESET__ + __A__.FORE_YELLOW
QUERY_BORDER                         = _RESET__ + __A__.FORE_BRIGHT_BLACK
QUERY_PROMPT                         = _RESET__ + __A__.FORE_YELLOW

# Progress bars
PROGRESS_SIMPLE                      = _RESET__ + __A__.FORE_CYAN
PROGRESS_CHAR_COLUMN_SEPARATOR       = _RESET__
PROGRESS_COLOUR_PROGRESS_SIDE        = _RESET__ + __A__.FORE_BRIGHT_BLACK + __A__.BACK_LIGHT_BLUE + __A__.DIM
PROGRESS_COLOUR_TITLE_COLUMN         = _RESET__ + __A__.FORE_BLACK + __A__.BACK_LIGHT_GREEN
PROGRESS_COLOUR_CURRENT_COLUMN       = _RESET__ + __A__.FORE_BLACK + __A__.BACK_LIGHT_BLUE
PROGRESS_COLOUR_TIME_COLUMN          = _RESET__ + __A__.FORE_BLACK + __A__.BACK_LIGHT_BLUE + __A__.DIM
PROGRESS_COLOUR_PROGRESS_POINT       = _RESET__ + __A__.BACK_WHITE + __A__.FORE_BLACK
PROGRESS_COLOUR_PROGRESS_SPACE_RIGHT = _RESET__ + __A__.BACK_WHITE + __A__.FORE_BRIGHT_BLACK

PROGRESS_COLOUR_PROGRESS_SPACE_LEFT_ARRAY = []
PROGRESS_COLOUR_PROGRESS_SPACE_LEFT_ARRAY.append( _RESET__ + __A__.BACK_RED + __A__.FORE_BRIGHT_RED )
PROGRESS_COLOUR_PROGRESS_SPACE_LEFT_ARRAY.append( _RESET__ + __A__.BACK_GREEN + __A__.FORE_BRIGHT_GREEN )
PROGRESS_COLOUR_PROGRESS_SPACE_LEFT_ARRAY.append( _RESET__ + __A__.BACK_BLUE + __A__.FORE_BRIGHT_BLUE )
PROGRESS_COLOUR_PROGRESS_SPACE_LEFT_ARRAY.append( _RESET__ + __A__.BACK_CYAN + __A__.FORE_BRIGHT_CYAN )
PROGRESS_COLOUR_PROGRESS_SPACE_LEFT_ARRAY.append( _RESET__ + __A__.BACK_MAGENTA + __A__.FORE_BRIGHT_MAGENTA )
PROGRESS_COLOUR_PROGRESS_SPACE_LEFT_ARRAY.append( _RESET__ + __A__.BACK_YELLOW + __A__.FORE_BRIGHT_YELLOW )
