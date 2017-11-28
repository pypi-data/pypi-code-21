def _print_line_informations(choices=None, default=None):
    if choices is not None:
        print('[%s]' % '/'.join([str(chc).upper()
                                 if chc == default else str(chc)
                                 for chc in choices]), end=' ')
    if default not in {'', None}:
        if choices and default not in choices:
            for new_default, value in choices.items():
                if value == default:
                    default = new_default
                    break
        print('(default: %r)' % default, end=' ')
    return default


def ask(text, choices=None, default=None, required=False, cast=str):
    choices = [] if choices is None else [cast(chc) for chc in choices]
    while True:
        print(text, end=' ')
        default = _print_line_informations(choices, default)
        print(':', end=' ')

        result = input()

        if cast is not None:
            try:
                result = cast(result)
            except ValueError:
                print("Couldn't cast %r to %r" % (result, cast))
                continue

        if not result and required:
            print('you must provide an answer')
        elif result and choices and result not in choices:
            print('%r is not in %r' % (result, choices))
        else:
            return result


def ask_bool(text, default=True, required=False):
    default = 'yes' if default else 'no'
    result = ask(text, choices=['y', 'yes', 'n', 'no'],
                 default=default, required=required, cast=str)
    if result.lower() in {'y', 'yes'}:
        return True
    return False
