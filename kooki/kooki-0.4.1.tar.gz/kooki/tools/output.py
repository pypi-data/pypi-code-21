from termcolor import colored

fixed_width = 80

def output_control(func):

    def wrapper(cls, *args, **kwargs):
        if cls.output:
            func(cls, *args, **kwargs)

    return wrapper


class Output():

    color = True
    output = True
    debug = False

    @classmethod
    def _print_colored(cls, text='', color='blue', end='\n'):
        if cls.color:
            print(colored(text, color), end=end)
        else:
            print(colored(text), end=end)

    @classmethod
    def set_color_policy(cls, color):
        cls.color = color

    @classmethod
    def set_output_policy(cls, output):
        cls.output = output

    @classmethod
    def set_debug_policy(cls, debug):
        cls.debug = debug

    @classmethod
    @output_control
    def title(cls, name):
        cls.step(name, 'white', '-')

    @classmethod
    @output_control
    def start_command(cls, name):
        cls.step(name, 'white', '=', '[', ']')

    @classmethod
    @output_control
    def end_command(cls):
        cls.step('', 'white', '=', no_space=True)

    @classmethod
    @output_control
    def start_step(cls, name):
        cls.step(name, 'yellow', '-')

    @classmethod
    @output_control
    def error_step(cls, name):
        cls.step(name, 'red', '-')

    @classmethod
    def step(cls, name, text_color, character, before='', after='', no_space=False):

        str_size = len(name)

        if (str_size % 2) == 0:
            number_of_dash_left = int((fixed_width - str_size) / 2)
            number_of_dash_right = number_of_dash_left

        else:
            number_of_dash_left = int((fixed_width - str_size) / 2)
            number_of_dash_right = number_of_dash_left + 1

        number_of_dash_left -= len(before)
        number_of_dash_right -= len(after)

        space = ' '
        if no_space:
            space = ''
            number_of_dash_left += 1
            number_of_dash_right += 1

        dash_left = ''
        for i in range(0, number_of_dash_left):
            dash_left += character
        dash_left += before

        dash_right = after
        for i in range(0, number_of_dash_right):
            dash_right += character

        cls._print_colored('{0}{3}{1}{3}{2}'.format(dash_left, name, dash_right, space), text_color)

    @classmethod
    @output_control
    def category(cls, message):
        cls._print_colored('[' + message + ']', 'magenta')

    @classmethod
    @output_control
    def error(cls, message):
        cls._print_colored(message, 'red')

    @classmethod
    @output_control
    def warning(cls, message):
        cls._print_colored(message, 'orange')

    @classmethod
    @output_control
    def info(cls, message):
        cls._print_colored(message, 'cyan')

    @classmethod
    @output_control
    def infos(cls, infos, attrs):

        text = ''
        spaces = {}
        shift = 2

        for info in infos:
            for attr in attrs:
                name = attr[0]
                if name in spaces:
                    if len(info[name]) + shift > spaces[name]:
                        spaces[name] = len(info[name]) + shift
                else:
                    spaces[name] = len(info[name]) + shift

        for info in infos:
            for attr in attrs:
                name = attr[0]
                color = attr[1]
                text = ''
                if len(attr) > 2:
                    text = attr[2]

                if isinstance(info[name], tuple):
                    full_text = text + info[name][0]
                    color = info[name][1]
                else:
                    full_text = text + info[name]

                cls._print_colored(full_text, color, end='')
                cls._print_colored(' ' * (spaces[name] - len(info[name])), end='')
            cls._print_colored()
