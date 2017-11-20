"""CLI for pynclose.

"""

import inclose
from . import cli, export


if __name__ == "__main__":
    args = cli.parse_args()
    atoms = export.asp_from_context(args.infile, args.min_ext, args.min_int)
    if args.outfile:
        with open(args.outfile, 'w') as fd:
            fd.write('\n'.join(atoms))
    else:  # goto stdout
        print('\n'.join(atoms))
