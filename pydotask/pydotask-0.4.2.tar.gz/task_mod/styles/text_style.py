from .termcolor import colors

#Temporary
version = '0.4 ALPHA'

def hellotext():

    print('\a')
    print(colors.fg.lightcyan + '   ______       _____        ')
    print('  (_____ \     (____ \       ')
    print('   _____) )   _ _   \ \ ___  ')
    print('  |  ____/ | | | |   | / _ \ ')
    print('  | |    | |_| | |__/ / |_| |')
    print('  |_|     \__  |_____/ \___/ ')
    print('         (____/              ' + colors. reset + colors.bold + version + colors.reset)

    return None


def command_help():

    print('\a')
    print(colors.bold + ' Commands :' + colors.reset)
    print('\a')
    print(colors.fg.lightgreen + ' add (-a)' + colors.reset + ' ......... Create new task')
    print(colors.fg.lightgreen + ' remove (-r)' + colors.reset + ' ...... Remove available task')
    print(colors.fg.lightgreen + ' show (-s)'+ colors.reset +' ........ Show all available tasks')
    print(colors.fg.lightgreen + ' clear (-c)'+ colors.reset +' ....... Clears the Terminal')
    print(colors.fg.lightgreen + ' help (-h)'+ colors.reset +' ........ Open the help menu')
    print(colors.fg.lightgreen + ' quit (-q)'+ colors.reset +' ........ Quit PyDo' + colors.reset)
    print('\a')
