#!python
from optparse import OptionParser
from os.path import exists

import mmf_setup

# List of (variable, value, filename)
# Will print a statement like the following iff filename is None or exists:
#
#    export variable=value
#
VARIABLES = [
    ('MMF_SETUP', mmf_setup.MMF_SETUP, mmf_setup.MMF_SETUP),
    ('HGRCPATH', ':'.join(['${HGRCPATH:-~/.hgrc}', mmf_setup.HGRC]), mmf_setup.HGRC),
]


def run(debug=False):
    env = []
    for var, value, filename in VARIABLES:
        if not filename or exists(filename):
            env.append('export {var}="{value}"'.format(var=var, value=value))
        elif debug:
            print("# processing {}={} failed:\n   no file '{}'"
                  .format(var, value, filename))

    print("\n".join(env))


parser = OptionParser()
parser.add_option("-d", "--debug",
                  action="store_true", dest="debug", default=False,
                  help="debug missing files")

if __name__ == '__main__':
    (options, args) = parser.parse_args()
    run(options.debug)
