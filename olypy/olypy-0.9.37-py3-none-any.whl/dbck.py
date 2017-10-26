'''
Database checker, similar to the one in the C code (check.c)
'''
import sys

from .oid import to_oid
from . import box
from . import details
from .formatters import grand_format


def check_firstline(data, fix, checknames=False):
    '''Make sure everything in data has a firstline'''
    problem = 0
    for k, v in data.items():
        if not isinstance(v, dict) or 'firstline' not in v:
            print('Thing {} has no firstline'.format(k), file=sys.stderr)
            problem += 1
            # cannot be fixed
        elif checknames and ' unform ' not in v['firstline'][0] and 'na' not in v:
            print('Thing {} has no name'.format(v['firstline']), file=sys.stderr)
            if fix:
                _, _, kind = v['firstline'][0].split(' ', 2)
                data[k]['na'] = [kind[0].upper() + kind[1:]]
                print('   fixed.', file=sys.stderr)
            else:
                problem += 1
    return problem


def check_boxes(data):
    problem = 0
    for k, v in data.items():
        for k1, v1 in v.items():
            if k1 not in grand_format:
                print('Thing {} has unknown section {}'.format(k, k1), file=sys.stderr)
                problem += 1
            elif isinstance(v1, list):
                if len(v1) > 1 and grand_format[k1] == 1:
                    print('Thing {} {} is a multi-item list {} but should have 1 entry'.format(k, k1, v1),
                          file=sys.stderr)
                    problem += 1
            elif isinstance(v1, dict):
                if not isinstance(grand_format[k1], dict):
                    print('Thing {} {} is a dict but should not be'.format(k, k1), file=sys.stderr)
                    problem += 1
                    continue
                for k2, v2 in v1.items():
                    if k2 not in grand_format[k1]:
                        print('Thing {} {} has unknown section {}'.format(k, k1, k2), file=sys.stderr)
                        problem += 1
                    elif isinstance(v2, list):
                        if len(v2) > 1 and grand_format[k1][k2] == 1:
                            print('Thing {} {} {} is a multi-item list {} but should have 1 entry'.format(k, k1, k2, v2),
                                  file=sys.stderr)
                            problem += 1
                    else:
                        print('Thing {} {} has a bad value'.format(k, k1, k2), file=sys.stderr)
                        problem += 1
            else:
                print('Box {} {} has bad value {}'.format(k, k1, v1), file=sys.stderr)
                problem += 1
    return problem


where_things = set(('loc', 'ship', 'char'))


def check_where_here(data, fix=False):
    '''Make sure that every box that's where is here, and here is where.
    Does not check anything that is not where.'''
    problem = 0
    for k, v in data.items():
        if 'firstline' in v and ' loc region' not in v['firstline'][0]:
            _, kind, _ = v['firstline'][0].split(' ', maxsplit=2)
            if kind in where_things:
                try:
                    where = data[k]['LI']['wh'][0]
                except (KeyError, IndexError):
                    print('Thing {} is not anywhere'.format(k), file=sys.stderr)
                    print('  ', data[k]['firstline'][0], file=sys.stderr)
                    problem += 1
                    continue
                try:
                    hl = data[where]['LI']['hl']
                    hl.index(k)
                except (KeyError, ValueError):
                    print('Thing {} is not in here list of thing {}'.format(k, where), file=sys.stderr)
                    print('  ', data[k]['firstline'][0], file=sys.stderr)
                    if fix and where in data:
                        print('  ', data[where]['firstline'][0], file=sys.stderr)
                        box.subbox_append(data, where, 'LI', 'hl', k, dedup=True)
                        print('   fixed.', file=sys.stderr)
                    else:
                        problem += 1
                    continue

    for k, v in data.items():
        if 'LI' in v:
            if 'hl' in v['LI']:
                hl = v['LI']['hl']
                for unit in hl:
                    try:
                        where = data[unit]['LI']['wh'][0]
                        if where != k:
                            raise ValueError
                    except (KeyError, ValueError, IndexError):
                        print('Unit {} is in here list of unit {}, but is not there'.format(unit, k), file=sys.stderr)
                        if unit not in data:
                            print('   btw unit {} does not exist'.format(unit), file=sys.stderr)
                        if fix:
                            box.subbox_remove(data, k, 'LI', 'hl', unit)
                            print('   fixed.', file=sys.stderr)
                        else:
                            problem += 1

    return problem


def check_faction_units(data, fix=False):
    '''
    If a box is in a faction, make sure it's on the faction's unit list and vice versa.
    Also check that a pledge target exists. Fix.
    '''
    problem = 0
    for k, v in data.items():
        if 'CH' in v:
            if 'lo' in v['CH']:
                fact = v['CH']['lo'][0]
                try:
                    un = data[fact]['PL']['un']
                    un.index(k)
                except (KeyError, ValueError):
                    print('Unit {} is in faction {} but not vice versa'.format(k, fact), file=sys.stderr)
                    print('  ', v['firstline'][0], file=sys.stderr)
                    problem += 1
            if 'CM' in v and 'pl' in v['CM']:
                pledged_to = v['CM']['pl'][0]
                if pledged_to not in data or ' char ' not in data[pledged_to]['firstline'][0]:
                    print('Unit {} is pledged to {}, who does not exist or is not a char'.format(k, pledged_to), file=sys.stderr)
                    if fix:
                        print('  fixed.', file=sys.stderr)
                        del v['CM']['pl']
                    else:
                        problem += 1

    for k, v in data.items():
        if ' player ' in v['firstline'][0] and 'un' in v['PL']:
            for unit in v['PL']['un']:
                try:
                    lo = data[unit]['CH']['lo'][0]
                    if lo != k:
                        raise ValueError
                        print('lo {} i {}'.format(lo, k), file=sys.stderr)
                except (KeyError, ValueError):
                    print('Unit {} is not in faction {}'.format(unit, k), file=sys.stderr)
                    if unit in data:
                        print('  ', data[unit]['firstline'][0], file=sys.stderr)
                    else:
                        print('  ' 'unit {} is not in data'.format(unit), file=sys.stderr)
                    problem += 1
                    continue

    return problem


def check_unique_items(data):
    "Make sure unique items exist on exactly one inventory list, somewhere."
    problem = 0
    all_unique_items = {}
    for k, v in data.items():
        if int(k) > 399 and ' item ' in v['firstline'][0]:
            if ' item tradegood' in v['firstline'][0]:
                continue
            all_unique_items[k] = 1
            try:
                un = None
                un = v['IT']['un'][0]
                il = data[un]['il']
                if not isinstance(il, list):
                    print('Whoops. id', k, 'il is', il, file=sys.stderr)
                il.index(k)  # this might have false positive and match a qty XXX
            except (KeyError, ValueError):
                print('Unique item {} is not in inventory of unit {}'.format(k, un), file=sys.stderr)
                print('  ', v['firstline'][0], file=sys.stderr)
                if un in data:
                    print('  ', data[un]['firstline'][0], file=sys.stderr)
                problem += 1
                continue

    all_inventory = {}
    for k, v in data.items():
        if 'il' in v:
            il = v['il'].copy()
            while len(il) > 0:
                item = il.pop(0)
                qty = int(il.pop(0))
                all_inventory[item] = all_inventory.get(item, 0) + qty

    for i in all_unique_items:
        if i not in all_inventory or all_inventory[i] != 1:
            print('Unique item {} does not have exactly one instance'.format(i), file=sys.stderr)
            if i in data:
                print('  ', data[i]['firstline'][0], file=sys.stderr)
            problem += 1
            continue

    for i in all_inventory:
        if int(i) > 399 and i not in data:
            print('Item {} is in inventory somewhere but is not in data'.format(i), file=sys.stderr)
            problem += 1

    return problem


def check_moving(data):
    '''
    Make sure moving stack leaders have a running move or fly command cs=2
    If I'm a moving non-stack-leader make sure my CH mo == stack leader CH mo
    sailing: check SL mo of ship; character has no CH mo
    '''
    problem = 0
    stacks = {}

    pass

    for k, v in data.items():
        if ' ship ' in v['firstline'][0]:
            if v.get('SL', {}).get('mo', [False])[0]:
                captain = v.get('LI', {}).get('hl', [None])[0]
                if captain is None:
                    print('Ship {} is moving but lacks a captain'.format(k), file=sys.stderr)
                    problem += 1
                    continue
                CO = data[captain].get('CO', {})
                if CO.get('cs', [None])[0] != '2' or not CO.get('li', [''])[0].lower().startswith('sail '):
                    print('Ship {} captain {} is not sailing'.format(k, captain), file=sys.stderr)
                    problem += 1
                    continue
                if data[captain]['CH'].get('mo', [None])[0]:
                    print('Ship {} captain {} is moving, should not be'.format(k, captain), file=sys.stderr)
                    problem += 1
                    continue

    return problem


def check_prisoners(data):
    "Make sure prisoners are stacked under another character"
    problem = 0
    for k, v in data.items():
        if ' char ' in v['firstline'][0]:
            if 'CH' in v:
                if 'pr' in v['CH']:
                    where = v['LI']['wh'][0]
                    if ' char ' not in data[where]['firstline'][0]:
                        print('Prisoner {} is not stacked; location {}'.format(to_oid(k), where), file=sys.stderr)
                        problem += 1
    return problem


def check_links(data, fix=False):
    '''
    Regression test.
    Make sure provinces don't link cities in LO pd.
    Make sure cities don't have LO pd.
    TODO: roads
    TODO: sewers, cities
    TODO: graveyards and faery hills
    '''
    problem = 0

    for k, v in data.items():
        fl = v['firstline'][0]
        if ' loc ' in fl:
            kind = fl.partition(' loc ')[2]
            if kind in details.province_kinds:
                if 'LO' not in v or 'pd' not in v['LO']:
                    print('Province {} lacks LO pd'.format(k), file=sys.stderr)
                    problem += 1
                    continue
                pd = v['LO']['pd']
                for route in pd:
                    if route != '0':
                        if route not in data:
                            print('Province {} has a route to {}, which does not exist'.format(k, route),
                                  file=sys.stderr)
                            if fix:
                                print('  fixed.', file=sys.stderr)
                                v['LO']['pd'] = ['0' if x == route else x for x in pd]
                            else:
                                problem += 1
                            continue
                        route_fl = data[route]['firstline'][0]
                        if route_fl.endswith(' loc city'):
                            # turnparser-generated dbs used to have this problem
                            print('Province {} has a NESWUD link to city {}'.format(k, route), file=sys.stderr)
                            problem += 1
            elif kind == 'city':
                pd = v.get('LO', {}).get('pd', [])
                for dir, route in enumerate(pd):
                    if int(dir) < 4 and route != '0':
                        print('City {} has NESW link'.format(k), file=sys.stderr)
                        problem += 1
    return problem


def check_db(data, fix=False, checknames=False):
    problems = 0
    problems += check_firstline(data, fix, checknames=checknames)
    problems += check_boxes(data)
    problems += check_where_here(data, fix)
    problems += check_faction_units(data, fix)
    problems += check_unique_items(data)
    problems += check_moving(data)
    problems += check_prisoners(data)
    problems += check_links(data, fix)

    return problems
