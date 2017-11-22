'''
Helpers to the UNIX shell.
'''
from subprocess import Popen, PIPE


def run(command):
    '''
    Run an arbitrary shell command.
    USAGE: run('ls -la')
    '''
    argv = command.split(' ')

    with Popen(argv, bufsize=1, stdout=PIPE, stderr=PIPE, universal_newlines=True) as process:
        out, err = process.communicate()
        return (process.returncode, out, err)


def whoami():
    ''' Returns the output of `whoami` UNIX command. '''
    _, out, _ = run('whoami')

    return out.rstrip()
