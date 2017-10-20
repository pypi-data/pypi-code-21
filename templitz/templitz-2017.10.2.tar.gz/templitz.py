""" Generate new files from templates. """
import argparse
import sys
from typing import Optional
from contextlib import contextmanager
import os
from itertools import chain
from cjrh_template import Template
import biodome


__version__ = '2017.10.2'


@contextmanager
def file_or_stdout(args):
    paths = biodome.environ.get('TEMPLITZ_PATH', '').split(os.pathsep)
    for path, hit in all_templates(args):
        if args.template in hit:
            break
    else:
        raise FileNotFoundError('Template not found!')

    if args.stdout:
        f = sys.stdout
    else:
        # Remove the trailing ".templitz"
        fname = hit.rpartition('.')[0]
        target = os.path.join(args.outdir, fname)
        f = open(target, 'w+')
    try:
        yield f
    finally:
        if f is not sys.stdout:
            f.close()


def all_templates(args):
    paths = biodome.environ.get('TEMPLITZ_PATH', '').split(os.pathsep)
    # Current dir first, and /library of templitz.py dir as last resort
    paths = chain(
        [os.getcwd()],
        paths,
        [os.path.join(os.path.dirname(__file__), 'library')]
    )
    for p in paths:
        if not os.path.exists(p):
            continue
        for fname in os.listdir(p):
            if fname.endswith('.templitz'):
                yield p, fname


def load_template(args):
    paths = biodome.environ.get('TEMPLITZ_PATH', '').split(os.pathsep)
    for path, hit in all_templates(args):
        if args.template in hit:
            break
    else:
        msg = (f'Error: template "{args.template}" not found in any of '
               f'the following locations:')
        msg += '\n'.join(paths)
        raise FileNotFoundError(msg)

    with open(os.path.join(path, hit)) as f:
        data = f.read()

    return Template(data)


def subs(args):
    tmpl = load_template(args)
    params = {
        x.partition('=')[0]: x.partition('=')[2] for x in args.params
    }
    output = tmpl.safe_substitute(params)
    with file_or_stdout(args) as f:
        f.write(output)


def info(args):
    tmpl = load_template(args)
    print('The template has the following vars: ')
    print()
    for ph in tmpl.placeholders():
        print('   ${%s}' % ph)
    print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--template')
    parser.add_argument('-i', '--info', help='Information about the templit.',
                        action='store_true')
    parser.add_argument(
        '-l', '--list', help='List all available templitz.',
        action='store_true'
    )
    parser.add_argument('-s', '--stdout', action='store_true',
                        help='Write to stdout instead of file.')
    parser.add_argument('-o', '--outdir', help='Output directory.',
                        default=os.getcwd())
    parser.add_argument(
        '-p', '--params', nargs='+', default=[]
    )
    args = parser.parse_args()
    print(args.params)
    try:
        if args.info:
            info(args)
        elif args.list:
            for path, fname in all_templates(args):
                print(path, fname)
        else:
            subs(args)
    except FileNotFoundError as e:
        print(f'Error: {e!s}')


if __name__ == '__main__':
    main()
