""" Generate new files from templates. """
import argparse
import sys
from typing import Optional
from contextlib import contextmanager
import os
import shlex
from itertools import chain
from cjrh_template import Template
import biodome


__version__ = '2017.10.3'


@contextmanager
def file_or_stdout(args, filename: Optional[str] = None):
    """If target_filename is None, just strip off the .templitz
    extension off args.template and used that as the target name."""
    for path, hit in all_templates(args):
        if args.template in hit:
            break
    else:
        raise FileNotFoundError('Template not found!')

    if args.stdout:
        f = sys.stdout
    else:
        # Remove the trailing ".templitz"
        fname = filename or hit.rpartition('.')[0]
        target = os.path.join(args.outdir, fname)
        f = open(target, 'w+')
    try:
        yield f
    finally:
        if f is not sys.stdout:
            f.close()


def all_templates(args):
    pathstr: str = biodome.environ.get('TEMPLITZ_PATH', '').split(os.pathsep)
    # Current dir first, and /library of templitz.py dir as last resort
    paths = chain(
        [os.getcwd()],
        pathstr,
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

    # Strip out lines starting with "#templitz" and process settings in
    # them.
    settings = {}
    final_lines = []
    for line in output.splitlines(False):
        if line.startswith('#templitz'):
            data = line.partition('#templitz')[2]
            for item in shlex.split(data):
                key, _, value = item.partition('=')
                # Handle toggles/bools automatically
                settings[key] = value.strip('"') or True
        else:
            final_lines.append(line)

    output = '\n'.join(final_lines)
    filename = settings.get('filename')
    with file_or_stdout(args, filename=filename) as f:
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
