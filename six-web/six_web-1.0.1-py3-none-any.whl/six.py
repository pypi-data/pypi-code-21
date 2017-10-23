import sys


def add(a, b):
    return a + b


def haha():
    print("xx")


class Six(object):
    def __init__(self):
        pass


def _cli_parse(args):
    '''
        python -m six_web 输出的帮助文档
    :param args: 参数输入
    :return:
    '''
    from argparse import ArgumentParser
    parser = ArgumentParser(prog=args[0], usage="%(prog)s [options] package.moudle:app",
                            epilog='Life is short, love python!',
                            description='Coding to change the world for better.')
    opt = parser.add_argument
    opt('-v', '--version', action='store_true', help='show version number')
    opt('-b', '--bind', metavar='ip:port', help='bind address, default localhost:8080')
    opt('-s', '--server', metavar='SERVER', help='user SERVER as backend')
    opt('-C', '--param', metavar='NAME=VALUE', help='overwrite config value')
    opt('--debug', help='run server in debug mode')
    opt('--reload', help='auto reload on file changes')
    parser.parse_args()


if __name__ == '__main__':
    _cli_parse(sys.argv)
