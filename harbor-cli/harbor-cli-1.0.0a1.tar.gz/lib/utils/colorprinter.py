from colorama import init, Fore, Style

# Init colorama.
init()

# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Style: DIM, NORMAL, BRIGHT, RESET_ALL
def colorprint(text_color, bail_result=False):
    '''
    Colorprint text into the console. Call it as a curried function.

    greenPrinter = colorprinter('GREEN')
    greenPrinter('this will be green')

    OR:

    colorprint('GREEN')('this will be green')
    '''
    def printer(text):
        ''' This actually does the printing part. Allows for reusable color printers. '''
        color = Fore.GREEN if text_color == 'GREEN' else Fore.RED
        if not bail_result:
            print(color + text)
            print(Style.RESET_ALL)
        else:
            return color + text

    return printer
