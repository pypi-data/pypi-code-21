import sys

from lark import Lark



def main():
    if len(sys.argv) < 2:
        print('bla')
        return

    fn, = sys.argv[1:]
    with open(fn) as f:
        grammar = f.read()

    lark = Lark(grammar, parser='lalr')

    import pdb
    pdb.set_trace()


if __name__ == '__main__':
    main()
