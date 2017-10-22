import sys

palette = {
    'black': '\033[30m',
    'red': '\033[91m',
    'green': '\033[92m',
    'yellow': '\033[93m',
    'blue': '\033[94m',
    'magenta': '\033[95m',
    'cyan': '\033[96m',
    'white': '\033[97m',
    'gray': '\033[37m',
    'default': '\033[0m',
}

highlighter = {
    'black': '\033[40m',
    'red': '\033[101m',
    'green': '\033[102m',
    'yellow': '\033[103m',
    'blue': '\033[104m',
    'magenta': '\033[105m',
    'cyan': '\033[106m',
    'white': '\033[107m',
    'gray': '\033[47m',
}

# formatter = {                   # TODO: This isn't being used at the moment.
#     'default': '\033[0m',
#     'bold': '\033[1m',
#     'faint': '\033[2m',
#     'italic': '\033[3m',        # Doesn't work on Ubuntu/Mac terminal.
#     'underline': '\033[4m',
#     'blinking': '\033[5m',
#     'fast_blinking': '\033[6m', # Doesn't work on Ubuntu/Mac terminal.
#     'reverse': '\033[7m',       # Note: This reverses the back-/foreground color.
#     'hide': '\033[8m',
#     'strikethrough': '\033[9m', # Doesn't work on Ubuntu/Mac terminal.
# }

def color_print(s, color=None, highlight=None):
    """
    From http://stackoverflow.com/a/287944/610569
    See also https://gist.github.com/Sheljohn/68ca3be74139f66dbc6127784f638920
    """
    if color in palette and color != 'default':
        s = palette[color] + s
    # Highlight / Background color.
    if highlight and highlight in highlighter:
        s = highlighter[highlight] + s
    # Custom string format.
    # for name, value in kwargs.items():
    #     if name in formatter and value == True:           # TODO: Add support to method implementations.
    #         s = formatter[name] + s
    print(s + palette['default'] + '\n') #, file=sys.stdout)

def string_constructor(args):
    res = ""

    for arg in args:
        res += arg

    return res


"""
    Here are the useable methods.
"""

def info(*args):
	color_print(string_constructor(args), color='cyan')

def mega_info(*args):
	color_print(string_constructor(args), color='white', highlight='cyan')

def warning(*args):
	color_print(string_constructor(args), color='yellow')

def mega_warning(*args):
	color_print(string_constructor(args), color='black', highlight='yellow')

def error(*args):
	color_print(string_constructor(args), color='red')

def mega_error(*args):
	color_print(string_constructor(args), color='white', highlight='red')

def success(*args):
	color_print(string_constructor(args), color='green')

def mega_success(*args):
	color_print(string_constructor(args), color='black', highlight='green')


def default(*args):
    color_print(string_constructor(args), color='default')

def custom(arg, customColor=None, backgroundColor=None):
    color_print(arg, color=customColor, highlight=backgroundColor)

def test():
    """A test method to print out examples."""
    print("")
    print("pybugger.pybugger2.success(*lyric)")
    success("\"We're no strangers to love,")
    print("")
    print("pybugger.pybugger2.mega_success(*lyric)")
    mega_success("You know the rules and so do I")
    print("")
    print("pybugger.pybugger2.info(*lyric)")
    info("A full commitment's what I'm thinking of")
    print("")
    print("pybugger.pybugger2.mega_info(*lyric)")
    mega_info("You wouldn't get this from any other guy")
    print("")
    print("pybugger.pybugger2.warning(*lyric)")
    warning("I just wanna tell you how I'm feeling")
    print("")
    print("pybugger.pybugger2.mega_warning(*lyric)")
    mega_warning("Gotta make you understand,")
    print("")
    print("pybugger.pybugger2.error(*lyric)")
    error("Never gonna give you up")
    print("")
    print("pybugger.pybugger2.mega_error(*lyric)")
    mega_error("Never gonna let you down")
    print("")
    print("pybugger.pybugger2.default(*lyric)")
    default("Never gonna round around")
    print("")
    print("pybugger.pybugger2.custom(lyric, \'magenta\', \'blue\')")
    custom("and desert you.\"", 'magenta', 'blue')