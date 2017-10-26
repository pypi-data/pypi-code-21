'''
Code to print Olympia item names, singular and plurall
'''

items = {
    '1': 'gold',
    '10': 'peasant',
    '11': 'worker',
    '12': 'soldier',
    '13': 'archer',
    '14': 'knight',
    '15': 'elite guard',
    '16': 'pikeman',
    '17': 'blessed soldier',
    '18': 'ghost warrior',
    '19': 'sailor',
    '20': 'swordsman',
    '21': 'crossbowman',
    '22': 'elite archer',
    '23': 'angry peasant',
    '24': 'pirate',
    '25': 'elf',
    '26': 'spirit',
    '31': 'undead',
    '32': 'savage',
    '33': 'skeleton',
    '34': 'barbarian',
    '51': 'wild horse',
    '52': 'riding horse',
    '53': 'warmount',
    '54': 'winged horse',
    '55': 'nazgul',
    '59': 'floatsam',
    '60': 'battering ram',
    '61': 'catapult',
    '62': 'siege tower',
    '63': 'ratspider venom',
    '64': 'lana bark',
    '65': 'avinia leaf',
    '66': 'spiny root',
    '67': 'farrenstone',
    '68': 'yew',
    '69': 'elfstone',
    '70': 'mallorn wood',
    '71': 'pretus bones',
    '72': 'longbow',
    '73': 'plate armor',
    '74': 'longsword',
    '75': 'pike',
    '76': 'ox',
    '77': 'wood',
    '78': 'stone',
    '79': 'iron',
    '80': 'leather',
    '81': 'ratspider',
    '82': 'mithril',
    '83': 'gate crystal',
    '84': 'blank scroll',
    '85': 'crossbow',
    '87': 'fish',
    '93': 'opium',
    '94': 'woven basket',
    '95': 'clay pot',
    '98': 'drum',
    '99': 'hide',
    '102': 'lead',
    '261': 'pitch',
    '271': 'centaur',
    '272': 'minotaur',
    '278': 'giant spider',
    '279': 'rat',
    '280': 'lion',
    '281': 'giant biard',
    '282': 'giant lizard',
    '283': 'bandit',
    '284': 'chimera',
    '285': 'harpie',
    '286': 'dragon',
    '287': 'orc',
    '288': 'gorgon',
    '289': 'wolf',
    '291': 'cyclops',
    '292': 'giant',
    '293': 'faery',
    '295': 'hound',
}

collective = set(('gold', 'undead', 'nazgul', 'floatsam', 'yew', 'wood', 'iron', 'mithril', 'fish',
                  'opium', 'lead', 'pitch', 'cyclops', 'lana bark', 'ratspider venom', 'plate armor',
                  'mallorn wood', 'pretus bones'))

unusual = {'man': 'men', 'elf': 'elves', 'ox': 'oxen', 'wolf': 'wolves', 'faery': 'faeries',
           'leaf': 'leaves'}


def item(i):
    return items.get(str(i), 'unknown')


def item_plural(i):
    i = item(i)
    if i in collective:
        return i
    if i in unusual:
        return unusual[i]
    for u in unusual:
        if i.endswith(u):
            return i.replace(u, unusual[u])
    return i + 's'
