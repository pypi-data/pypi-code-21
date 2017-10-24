#!/usr/bin/env python3

"""\
Save the results of the given command to a file such that someone can look at 
that file later and see how to rerun the command to produce the exact same 
results.

In particular, save the command line, repository URL, commit hash, and date 
along with the command output in the resulting file.  With this information, 
someone looking at this file at any point in the future should be able to 
checkout the exact same version of the script, run it with the exact same 
arguments, and confirm that they get the exact same result as before.

Usage:
    fossilize [<output> --] <command>...

Arguments:
    <output>
        If a -- is present in the command line, the first argument is taken to 
        be the name of the file to generate.  The default is `#_$.txt`.  `#` is 
        always replaced with today's date, and `$` is always replaced with the 
        base name of the command being run.

    <command> [<args>...]
        The command to run and preserve.
"""

def main():
    import sys
    from .api import fossilize

    # Do our own argument processing, because this command has an unusual 
    # interface.  We don't want to try to interpret options to <command>.

    if '-h' in sys.argv or '--help' in sys.argv or len(sys.argv) == 1:
        print(__doc__)
        raise SystemExit

    if len(sys.argv) > 2 and sys.argv[2] == '--':
        output = sys.argv[1]
        command = sys.argv[3:]

    else:
        output = None
        command = sys.argv[1:]

    fossilize(command, output)
