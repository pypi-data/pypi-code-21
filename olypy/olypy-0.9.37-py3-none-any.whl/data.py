'''
Code that manipulates the in-memory Olympia database
'''

from .oid import to_int, allocate_oid
from . import box


def loc_kind(data, who):
    try:
        _, _, kind = data[who]['firstline'][0].split(' ', 2)
    except KeyError:
        kind = ''
    return kind


def is_char(data, who):
    if ' char ' in data[who]['firstline'][0]:
        return True


def set_where(data, who, where, keep_children=False):
    who = to_int(who)
    promote_children = not keep_children
    unset_where(data, who, promote_children=promote_children)
    where = to_int(where)
    box.subbox_overwrite(data, who, 'LI', 'wh', where)
    box.subbox_append(data, where, 'LI', 'hl', who, dedup=True)


def unset_where(data, who, promote_children=True):
    '''
    If I'm somewhere, remove me from that somewhere.
    If promote_children & anyone is inside me, move them up.
    I may well end up nowhere... that will get cleaned up in the end.
    (Things that move can be nowhere... things that can't move should be destroyed XXXv0)
    '''
    if data.get(who) is None:
        return
    wh = data[who].get('LI', {}).get('wh', [None])[0]
    hl = data[who].get('LI', {}).get('hl')

    if wh is not None:
        del data[who]['LI']['wh']
        other_hl = data.get(wh, {}).get('LI', {}).get('hl')
        if other_hl is not None:
            try:
                other_hl.remove(who)
                data[wh]['LI']['hl'] = other_hl
            except ValueError:
                pass

    if promote_children and hl is not None and wh is not None:
        for child in hl:
            set_where(data, child, wh)

# XXXv0 can't have an endless loop of unlink->destroy->unlink
#    if not can_move(data, who):
#        destroy_box(data, who)


def can_move(data, who):
    '''
    Used for situations such as deciding to destroy or unwhere a no-longer-present box.
    Everything but locs can move.
    '''
    if ' loc ' not in data[who]['firstline'][0]:
        return True


def loop_here(data, where, fog=False):
    '''
    Make a list of everything here: chars, structures, sublocs. Do not descend into big sublocs (cities)
    If fog, make a list of only the visible things
    (caller responsible for making sure that fog=True only for provinces)
    '''
    hls = set()
    if 'LI' in data[where]:
        if 'hl' in data[where]['LI']:
            for w in data[where]['LI']['hl']:
                if fog and is_char(data, w):
                    continue
                hls.add(w)
                firstline = data[w]['firstline'][0]
                if ' loc city' in firstline:
                    # do not descend into cities
                    continue
                [hls.add(x) for x in loop_here(data, w)]
    return hls


def destroy_box(data, who, promote_children=True):
    '''
    Destroy a box that's become something different.
    '''
    if who not in data:
        return
    unset_where(data, who, promote_children=promote_children)
    # XXXv0 other links:
    # pledge chain - CM,pl is one-way so it needs a end-of-run fixup XXXv0
    # lord: CH,lo and previous lord CH,pl -- needs end-of-run fixup XXXv0
    lo = data[who].get('CH', {}).get('lo', [None])[0]
    if lo:
        box.subbox_remove(data, lo, 'PL', 'un', who)

    # unique items - need to look at firstline - IT,un is where it is
    # creater of things like storms, artifacts - IM,ct
    # owner of storm - MI,sb {summoned by}
    # storm bound to a ship - ship has SL,bs ... and the storm has MI,bs=itself (?)
    del data[who]


def upsert_box(data, newdata, who):
    '''
    Given a new box, figure out if an existing box needs to be destroyed.
    If it appears to be the same thing, merge the two boxes or overwrite the old one.
    '''


def upsert_char(data, newdata, who):
    '''
    Similar to upsert_box(), only for a character.
    '''
    pass


def upsert_location(data, newdata, top, promote_children=True):
    '''
    As we parse turns going forward in time, players observe locations.
    These might have been seen before, or may have changed. They may
    contain numerous structures, nobles, etc.
    '''

    # if not the same type, destroy the previous thing
    old_firstline = data.get(top, {}).get('firstline', '99999 nothing nothing')
    _, old_kind, old_subkind = old_firstline.split(' ', maxsplit=2)
    new_firstline = newdata[top]['firstline']
    _, new_kind, new_subkind = new_firstline.split(' ', maxsplit=2)
    # XXXv0 what about foo-in-progress to foo? lot of churn for castle with towers
    if old_kind != new_kind:
        if top in data:  # likely it is not
            raise ValueError('hey check this out')
            destroy_box(data, top, promote_children=promote_children)
        else:
            data[top] = {}

    data[top]['firstline'] = newdata[top]['firstline']
    data[top]['na'] = newdata[top]['na']

    oldhl = loop_here(data[top])
    newhl = loop_here(newdata[top])
    gone_or_new = oldhl.symmetric_difference(newhl)
    gone = gone_or_new.intersect(oldhl)
    new = gone_or_new.intersect(newhl)
    invisible_friends = set()
    if newdata[top].get('foggy'):
        invisible_friends = loop_here(data[top], fogonly=True)
        for i in list(invisible_friends):
            try:
                gone.remove(i)
            except KeyError:
                # this char is visible in newdata. remove from invisible.
                invisible_friends.remove(i)
    for g in list(gone):
        if data[g].get('LO', {}).get('hi'):
            # hidden sublocs never actually go away
            gone.remove(g)
    for g in gone:
        if can_move(data, g):
            unset_where(data, g)
        else:
            destroy_box(data, g)
    for n in new:
        upsert_box(data, newdata, n)

    # get current things to the right places - can just overwrite wh hl
    # thanks to the above processing of gone+new
    for lh in loop_here(newdata, top):
        hl = newdata[lh].get('LI', {}).get('hl', [])
        box.subbox_overwrite(data, lh, 'LI', 'hl', hl)
        for hll in hl:
            box.box_overwrite(data, hll, 'LI', 'wh', lh)
    for f in invisible_friends:
        # put these on the end, that's OK
        box.subbox_append(data, lh, 'LI', 'hl', f, dedup=True)

    for lh in loop_here(newdata, top):
        tl = newdata[lh].get('tl')
        if tl is not None:
            box.box_overwrite(data, lh, 'tl', tl)
    # mid-turn trade info
    #  XXXv1 don't trust any city *counts* but end-of-turn; city *prices* do not change
    #  XXXv1 do figure out if tradegoods have expired: 2 visible mid-turn means others have expired


def dead_char_body(data, who):
    '''
    Characters die mid-turn and become dead bodies. The previous
    turn end-state isn't quite right to freeze, but we'll do that for v0 XXXv1
    Location is province, or nowhere if at sea
    Province will be wrong if the char moved and died
    '''

    # XXXv1 melters, npcs don't get a body
    # XXXv0 set a location

    box.box_overwrite(data, who, 'firstline', str(who) + ' item dead body')
    box.subbox_overwrite(data, who, 'MI', 'sn', data[who]['na'])
    box.box_overwrite(data, who, 'na', 'dead body')
    pl = data[who]['CH']['lo']
    box.subbox_overwrite(data, who, 'MI', 'ol', pl)
    box.subbox_overwrite(data, who, 'IT', 'wt', 100)
    box.subbox_overwrite(data, who, 'IT', 'pl', 'dead bodies')

    # changing the firstline kind from char has consequences for the player thing
    # XXXv0 is this complete?
    # XXXv0 should I just let this get taken care of another way?
    box.subbox_remove(data, who, 'PL', 'un', who)
    box.subbox_remove(data, who, 'PL', 'kn', who)


def data_newbox(data, oid_kind, firstline, oid=None, overwrite=False):
    '''
    Create a new box. Intended for generating QA libs, not for parsing turns.
    (Turn parsing uses upserts.)
    '''
    if oid:
        oid = to_int(oid)  # roundtrips if already an int
    else:
        oid = allocate_oid(data, oid_kind)  # e.g. NNNN
    if oid in data:
        if not overwrite:
            raise ValueError(oid + ' is already in data')
        # if I am not the same thing, destory the old thing
        if data[oid]['firstline'] != firstline:
            destroy_box(data, oid)
    data[oid] = {}
    data[oid]['firstline'] = [str(oid) + ' ' + firstline]
    return oid


structures = {
    # in-progress: bm, er, eg ... bm runs 0..4
    'roundship': {'type': 'ship', 'de': 10, 'er': 50000, 'ca': 25000},
    'galley': {'type': 'ship', 'de': 20, 'er': 25000, 'ca': 5000},
    'inn': {'de': 10, 'er': 30000},
    'mine': {'de': 10, 'er': 50000, 'sd': 3, },  # depth is sd//3
    'temple': {'de': 10, 'er': 100000, 'te': 750},
    'tower': {'de': 40, 'er': 200000},
    'castle': {'de': 50, 'er': 1000000},
    'castle1': {'kind': 'castle', 'de': 55, 'er': 1000000, 'cl': 1},
    'castle2': {'kind': 'castle', 'de': 60, 'er': 1000000, 'cl': 2},
    'castle3': {'kind': 'castle', 'de': 65, 'er': 1000000, 'cl': 3},
    'castle4': {'kind': 'castle', 'de': 70, 'er': 1000000, 'cl': 4},
    'castle5': {'kind': 'castle', 'de': 75, 'er': 1000000, 'cl': 5},
    'castle6': {'kind': 'castle', 'de': 80, 'er': 1000000, 'cl': 6},
}


def add_structure(data, kind, where, name, progress=None, damage=None, defense=None, oid=None):
    if kind not in structures:
        raise ValueError
    where = to_int(where)
    if where not in data:
        raise ValueError('where ' + where + ' is not in data')

    oid = data_newbox(data, 'NNNN', structures[kind].get('type', 'loc') + ' ' +
                      structures[kind].get('kind', kind), oid=oid)
    set_where(data, oid, where)
    data[oid]['na'] = [name]

    # fully-finished structure
    if 'ca' in structures[kind]:
        box.subbox_overwrite(data, oid, 'SL', 'ca', structures[kind]['ca'])
    if 'cl' in structures[kind]:
        box.subbox_overwrite(data, oid, 'SL', 'cl', structures[kind]['cl'])
    if 'sd' in structures[kind]:
        box.subbox_overwrite(data, oid, 'SL', 'sd', structures[kind]['sd'])
    box.subbox_overwrite(data, oid, 'SL', 'de', defense or structures[kind]['de'])
    if damage:
        box.subbox_overwrite(data, oid, 'SL', 'da', damage)

    # XXX if under construction
    # remove ca if present
    # remove de
    # box.subbox_append(data, oid, 'SL', 'er', structures[kind]['er'])
    # compute eg
    # compute bm 0-4
    if progress:
        raise ValueError


def add_scroll(data, skill, unit, oid=None):
    oid = data_newbox(data, 'CNNN', 'item scroll', oid=oid)
    unit = to_int(unit)
    skill = str(skill)

    data[oid]['na'] = ['Scroll of '+skill]
    data[oid]['IT'] = {}
    data[oid]['IT']['wt'] = [1]
    data[oid]['IT']['un'] = [unit]
    data[oid]['IM'] = {}
    data[oid]['IM']['ms'] = [skill]

    box.box_append(data, unit, 'il', [oid, 1])


def add_potion(data, kind, im, unit, oid=None):
    oid = data_newbox(data, 'CNNN', 'item 0', oid=oid)
    unit = to_int(unit)

    data[oid]['na'] = ['Potion of '+kind]
    data[oid]['IT'] = {}
    data[oid]['IT']['wt'] = [1]
    data[oid]['IT']['un'] = [unit]
    data[oid]['IM'] = im

    box.box_append(data, unit, 'il', [oid, 1])
