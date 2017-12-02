COLORS = [
    'black',
    'red',
    'green',
    'yellow',
    'blue',
    'magenta',
    'cyan',
    'light_gray',
    'dark_gray',
    'light_red',
    'light_green',
    'light_yellow',
    'light_blue',
    'light_magenta',
    'light_cyan',
    'white'
]
STYLES = ['reset', 'bold', 'dim', 'italic', 'underlined']
COLOR_CODES = {color: index for index, color in enumerate(COLORS)}
STYLE_CODES = {style: index for index, style in enumerate(STYLES)}
SEQ_START = '\x1b['


def fg(color):
    return '{}38;5;{}m'.format(SEQ_START, COLOR_CODES[color])


def bg(color):
    return '{}48;5;{}m'.format(SEQ_START, COLOR_CODES[color])


def style(style_name):
    return '{}{}m'.format(SEQ_START, STYLE_CODES[style_name])
