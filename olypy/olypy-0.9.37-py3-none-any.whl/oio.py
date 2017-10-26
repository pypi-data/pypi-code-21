'''
Read and write Olympia state files.
'''

import os
import os.path
import sys
from contextlib import redirect_stdout

from .oid import to_oid
from .formatters import print_one_thing, read_oly_file


def fixup_ms(data):
    '''
    For whatever reason, the value in IM/ms needs to have a trailing space
    '''
    for box in data:
        if 'IM' in data[box]:
            if 'ms' in data[box]['IM']:
                value = data[box]['IM']['ms']
                value[0] = value[0].strip() + ' '
                data[box]['IM']['ms'] = value


def write_oly_file(data, kind=False, verbose=False):
    '''
    The main function that drives outputting a file
    '''

    fixup_ms(data)

    order = sorted([int(box) for box in data.keys()])

    count = 0
    for box in order:
        box = str(box)
        if kind:
            if ' '+kind+' ' not in data[box].get('firstline', '')[0]:
                continue
        print_one_thing(data[box])
        del data[box]
        count += 1

    if verbose:
        print('wrote', count, verbose, 'boxes.', file=sys.stderr)


def write_player(data, box, verbose=False):
    player_box = box
    boxlist = data[box].get('PL', {}).get('un', {})
    print_one_thing(data[box])
    del data[box]
    count = 0
    for box in boxlist:
        print_one_thing(data[box])
        del data[box]
        count += 1
    if verbose:
        print('wrote', count, 'characters for player', to_oid(int(player_box)), file=sys.stderr)


def read_players(dir, verbose=False):
    '''
    read every fie in dir whose name is an integer
    '''
    ret = {}
    files = os.listdir(dir)
    for name in files:
        if name.isdigit():
            data = read_oly_file(os.path.join(dir, name), verbose='player ' + name)
            ret.update(data)
    return ret


def write_players(data, dir, verbose=False):
    boxlist = list(data.keys())  # we're deleting as we go
    for box in boxlist:
        if data.get(box) is None:
            continue
        if ' player ' in data[box]['firstline'][0]:
            fact = os.path.join(dir, 'fact')
            if not os.path.isdir(fact):
                os.mkdir(fact)
            filename = os.path.join(dir, 'fact', box)
            with open(filename, 'w') as f:
                with redirect_stdout(f):
                    write_player(data, box, verbose=verbose)


def write_system_file(data):
    fr = None
    lt = 1
    tr = None
    ur = None
    hr = None
    hp = None
    nr = None
    nl = None
    cr = None
    for k, v in data.items():
        fl = v['firstline'][0]
        try:
            na = v['na'][0]
        except KeyError:
            na = ''
        if ' player pl_regular' in fl:
            lt = max(lt, int(v['PL']['lt'][0]))
        if fr is None and ' loc region' in fl and na == 'Faery':
            if v.get('LI', {}).get('hl'):
                fr = k
            else:
                fr = 0
        if tr is None and ' loc region' in fl and na == 'Undercity':
            if data[k].get('LI', {}).get('hl'):
                tr = k
            else:
                tr = 0
        if ur is None and ' loc region' in fl and na == 'Subworld':
            if data[k].get('LI', {}).get('hl'):
                ur = k
            else:
                ur = 0
        if hr is None and ' loc region' in fl and na == 'Hades':
            if data[k].get('LI', {}).get('hl'):
                hr = k
            else:
                hr = 0
        if hp is None and fl.endswith(' loc pit'):  # normal pits are 'pits'
            hp = k
        if nr is None and ' loc region' in fl and na == 'Nowhere':
            nr = k
            nl = v['LI']['hl'][0]
        if cr is None and ' loc region' in fl and na == 'Cloudlands':
            if data[k].get('LI', {}).get('hl'):
                cr = k
            else:
                cr = 0

    if hp is None:
        # not surprising for a player sim
        # if I wanted to do this right I have to also create City of the Dead in a provinces.
        # fake it.
        hp = hr

    days_per_month = 30
    days_since_epoch = lt * days_per_month

    system = '''sysclock: {} {} {}
indep_player=100
gm_player=200
skill_player=202
from_host=foo@example.com
reply_host=foo@example.com
game_title=SIMULATION
post=1
init=1
fr={}
tr={}
ur={}
fp=204
hr={}
hp={}
hl=205
nr={}
nl={}
np=206
cr={}
cp=210
'''.format(lt, days_per_month, days_since_epoch, fr, tr, ur, hr, hp, nr, nl, cr)
    if 'None' in system:
        raise ValueError('failed to find some stuff for system:\n' + system)
    print(system)


def read_lib(libdir):
    if not os.path.isdir(libdir):
        raise ValueError('libdir {} is not a directory'.format(libdir))
    data = read_oly_file(os.path.join(libdir, 'loc'), verbose='loc')
    data.update(read_oly_file(os.path.join(libdir, 'item'), verbose='item'))
    data.update(read_oly_file(os.path.join(libdir, 'skill'), verbose='skill'))
    data.update(read_oly_file(os.path.join(libdir, 'gate'), verbose='gate'))
    data.update(read_oly_file(os.path.join(libdir, 'road'), verbose='road'))
    data.update(read_oly_file(os.path.join(libdir, 'ship'), verbose='ship'))
    data.update(read_oly_file(os.path.join(libdir, 'unform'), verbose='unform'))
    data.update(read_oly_file(os.path.join(libdir, 'misc'), verbose='misc'))

    data.update(read_players(os.path.join(libdir, 'fact'), verbose=True))

    return data


def write_lib(data, libdir):
    if os.path.exists(libdir):
        if not os.path.isdir(libdir):
            raise ValueError('libdir {} is not a directory'.format(libdir))
    else:
        os.mkdir(libdir)

    with open(os.path.join(libdir, 'system'), 'w') as f:
        with redirect_stdout(f):
            write_system_file(data)

    with open(os.path.join(libdir, 'loc'), 'w') as f:
        with redirect_stdout(f):
            write_oly_file(data, kind='loc', verbose='loc')
    with open(os.path.join(libdir, 'item'), 'w') as f:
        with redirect_stdout(f):
            write_oly_file(data, kind='item', verbose='item')
    with open(os.path.join(libdir, 'skill'), 'w') as f:
        with redirect_stdout(f):
            write_oly_file(data, kind='skill', verbose='skill')
    with open(os.path.join(libdir, 'gate'), 'w') as f:
        with redirect_stdout(f):
            write_oly_file(data, kind='gate', verbose='gate')
    with open(os.path.join(libdir, 'road'), 'w') as f:
        with redirect_stdout(f):
            write_oly_file(data, kind='road', verbose='road')
    with open(os.path.join(libdir, 'ship'), 'w') as f:
        with redirect_stdout(f):
            write_oly_file(data, kind='ship', verbose='ship')
    with open(os.path.join(libdir, 'unform'), 'w') as f:
        with redirect_stdout(f):
            write_oly_file(data, kind='unform', verbose='unform')

    write_players(data, libdir, verbose=True)

    with open(os.path.join(libdir, 'misc'), 'w') as f:
        with redirect_stdout(f):
            write_oly_file(data, verbose='misc')  # catchall
