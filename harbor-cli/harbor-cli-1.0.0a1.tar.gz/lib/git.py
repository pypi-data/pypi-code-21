''' Git helpers. '''

from lib.shell import run


def branch():
    ''' Get current git branch. '''
    _, out, _ = run('git name-rev --name-only HEAD')

    return out.rstrip()


def username():
    ''' Get git username. '''
    _, out, _ = run('git config user.name')

    return out.rstrip()


def email():
    ''' Get git email. '''
    _, out, _ = run('git config user.email')

    return out.rstrip()
