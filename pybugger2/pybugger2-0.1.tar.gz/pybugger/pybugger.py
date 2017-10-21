from pybugger.lazyme.string import color_print

def string_constructor(args):
    res = ""

    for arg in args:
        res += arg

    return res

def info(*args):
    color_print(string_constructor(args), color='white')

def warning(*args):
    color_print(string_constructor(args), color='yellow')

def error(*args):
    color_print(string_constructor(args), color='red')

def success(*args):
    color_print(string_constructor(args), color='green')

def custom(arg, customColor):
    color_print(arg, color=customColor)

def test():
    """A test method to print out examples."""
    print("")
    print("pybugger.success(*lyric)")
    success("\"Never gonna give you up,")
    print("")
    print("pybugger.info(*lyric)")
    info("Never gonna let you down,")
    print("")
    print("pybugger.warning(*lyric)")
    warning("Never gonna run")
    print("")
    print("pybugger.error(*lyric)")
    error("around and")
    print("pybugger.custom(lyric, \"brightmagenta\")")
    custom("desert you.\"", 'brightmagenta')

