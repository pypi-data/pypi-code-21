# World of Warcraft API Library
# by mostm
from io import BytesIO
import requests
from PIL import Image
import config
print('Lib-WoW:Init')
region_lock = 'EU'
api = {'EU': {'Character': {'Profile': 'https://eu.api.battle.net/wow/character/{realm}/{name}',
                            'Data': {'Races': 'https://eu.api.battle.net/wow/data/character/races',
                                     'Classes': 'https://eu.api.battle.net/wow/data/character/classes',
                                     'Achievements': 'https://eu.api.battle.net/wow/data/character/achievements'}},
              'Talents': 'https://eu.api.battle.net/wow/data/talents',
              'Guild': 'https://eu.api.battle.net/wow/guild/{realm}/{name}',
              'Render': 'http://render-eu.worldofwarcraft.com/character/{0}',
              'Achievement': 'https://eu.api.battle.net/wow/achievement/{0}',
              'Realm Status': 'https://eu.api.battle.net/wow/realm/status'
              }}


class Exceptions:
    class Error(Exception):
        pass

    class NotFound(Error):
        def __init__(self, what, where):
            self.what = what
            self.where = where

    class NotOk(Error):
        def __init__(self, what, where):
            self.what = what
            self.where = where


class Character:
    """
    Character
    :param name: Name of character
    :param realm: Realm where we can find specified character
    :param region: Region where we can find specified realm
    """

    def __init__(self, name=None, realm=None, region=region_lock):
        self.name = name
        self.realm = Realm.find(realm)
        self.region = region
        self.input = {'name': name, 'realm': realm}
        self.raw = {
            'default': self.get(),
            'guild': self.get(fields='guild')['guild'],
            'stats': self.get(fields='stats')['stats'],
            'items': self.get(fields='items')['items'],
            'titles': self.get(fields='titles')['titles']
        }
        self.guild = Guild(name=self.raw['guild']['name'], realm=self.realm)
        self.level = {'xp': self.raw['default']['level'], 'item': self.raw['items']['averageItemLevelEquipped']}
        self.race = Race.get(self.raw['default']['race'], locale=self.realm.locale)
        self.wow_class = Class.get(self.raw['default']['class'], locale=self.realm.locale)
        self.stats = self.raw['stats']
        self.title = self.current_title()
        if self.title is not None:
            self.full_name = self.current_title()['name'] % self.name
        else:
            self.full_name = self.name

    def get(self, fields=None):
        params = {'locale': self.realm.locale, 'apikey': config.blizzard_key}
        if fields is not None:
            params['fields'] = fields
        url = api[region_lock]['Character']['Profile']
        r = requests.get(url.format(realm=self.realm.name, name=self.name), params=params)
        if r.status_code != 200:
            if r.status_code == 404:
                raise Exceptions.NotFound('{}-{}'.format(self.name, self.realm.name), r.json())
            else:
                raise Exceptions.NotOk(r.status_code, r.json())
        return r.json()

    def render(self, needed='profile'):
        path = self.raw['default']['thumbnail']
        filename = '{0}-{1}-{2}.jpg'
        fn = None
        if needed == 'avatar':
            avatar = Image.open(BytesIO(requests.get(api[region_lock]['Render'].format(path)).content))
            fn = filename.format(self.realm.name, self.name, 'avatar')
            avatar.save(fn, format='JPEG')
            return fn
        elif needed == 'inset':
            avatar = Image.open(
                BytesIO(requests.get(api[region_lock]['Render'].format(path.replace('avatar', 'inset'))).content))
            fn = filename.format(self.realm.name, self.name, 'inset')
            avatar.save(fn, format='JPEG')
            return fn
        elif needed == 'profile':
            avatar = Image.open(
                BytesIO(requests.get(api[region_lock]['Render'].format(path.replace('avatar', 'profilemain'))).content))
            fn = filename.format(self.realm.name, self.name, 'profile')
            avatar.save(fn, format='JPEG')
        return fn

    def current_title(self):
        for title in self.raw['titles']:
            if title.get('selected'):
                return title
            continue
        return None


class Guild:
    """
    Guild
    """

    def __init__(self, name=None, realm=None, region=region_lock, members=False):
        self.name = name
        self.realm = realm
        self.region = region
        self.raw = {'raw': self.get()}
        if members:
            self.raw['members'] = self.get(fields='members')
            self.members = []
            for member in self.raw['members']['members']:
                self.members.append(self.Member(name=member['character']['name'], realm=realm, rank=member['rank'],
                                                level=member['character']['level']))

    def get(self, fields=None):
        params = {'locale': self.realm.locale, 'apikey': config.blizzard_key}
        if fields is not None:
            params['fields'] = fields
        url = api[region_lock]['Guild']
        r = requests.get(url.format(realm=self.realm.name, name=self.name), params=params)
        if r.status_code != 200:
            if r.status_code == 404:
                raise Exceptions.NotFound('{}-{}'.format(self.name, self.realm.name), r.json())
            else:
                raise Exceptions.NotOk(r.status_code, r.json())
        return r.json()

    class Member:

        def __init__(self, name=None, realm=None, region=region_lock, rank=None, level=None):
            self.name = name
            self.level = level
            self.realm = realm
            self.region = region
            self.rank = rank



class Achievement:
    """
    Achievement
    """

    def __init__(self, uid=None):
        self.id = uid
        try:
            data = self.get(uid=self.id)
            self.title = data['title']
            self.points = data['points']
            self.description = data['description']
            try:
                self.reward = data['reward']
            except KeyError:
                self.reward = None
        except Exception as error:
            raise error

    @staticmethod
    def get(uid=None, locale='ru_RU'):
        params = {'locale': locale, 'apikey': config.blizzard_key}
        url = api[region_lock]['Achievement']
        r = requests.get(url=url.format(uid), params=params)
        if r.status_code != 200:
            if r.status_code == 404:
                raise Exceptions.NotFound(uid, r.json())
            else:
                raise Exceptions.NotOk(r.status_code, r.json())
        else:
            return r.json()


class Race:
    def __init__(self, uid=None, mask=None, side=None, name=None):
        self.id = uid
        self.mask = mask
        self.side = side
        self.name = name

    @staticmethod
    def get(uid, locale='ru_RU'):
        params = {'locale': locale, 'apikey': config.blizzard_key}
        r = requests.get(url=api['EU']['Character']['Data']['Races'], params=params)
        if r.status_code != 200:
            raise Exceptions.NotOk(r.status_code, r.json())
        else:
            for race in r.json()['races']:
                if race['id'] == uid:
                    return Race(uid=race['id'], mask=race['mask'], side=race['side'], name=race['name'])
            raise Exceptions.NotFound(uid, r.json()['races'])

    @staticmethod
    def load(locale='ru_RU'):
        params = {'locale': locale, 'apikey': config.blizzard_key}
        r = requests.get(url=api['EU']['Character']['Data']['Races'], params=params)
        if r.status_code != 200:
            raise Exceptions.NotOk(r.status_code, r.json())
        else:
            race_list = []
            for race in r.json()['races']:
                race_list.append(Race(uid=race['id'], mask=race['mask'], side=race['side'], name=race['name']))
            return race_list

    @staticmethod
    def find(uid):
        for race in races:
            if race.id == uid:
                return race
        raise Exceptions.NotFound(uid, races)


class Realm:
    def __init__(self, utype=None, population=None, queue=None, status=None, name=None, slug=None, battlegroup=None,
                 locale=None, timezone=None, connected_realms=None):
        self.type = utype
        self.population = population
        self.queue = queue
        self.status = status
        self.name = name
        self.slug = slug
        self.battlegroup = battlegroup
        self.locale = locale
        self.timezone = timezone
        self.connected_realms = connected_realms

    @staticmethod
    def load(locale='ru_RU'):
        params = {'locale': locale, 'apikey': config.blizzard_key}
        r = requests.get(url=api['EU']['Realm Status'], params=params)
        if r.status_code != 200:
            raise Exceptions.NotOk(r.status_code, r.json())
        else:
            realm_list = []
            for realm in r.json()['realms']:
                realm_list.append(Realm(utype=realm['type'], population=realm['population'], queue=realm['queue'],
                                        status=realm['status'], name=realm['name'],
                                        slug=realm['slug'], battlegroup=realm['battlegroup'],
                                        locale=realm['locale'], timezone=realm['timezone'],
                                        connected_realms=realm['connected_realms']))
            return realm_list

    @staticmethod
    def find(name):
        for realm in realms:
            if realm.name == name or name in realm.slug:
                return realm
        raise Exceptions.NotFound(name, realms)


class Class:
    def __init__(self, uid=None, mask=None, power_type=None, name=None):
        self.uid = uid
        self.mask = mask
        self.power_type = power_type
        self.name = name

    @staticmethod
    def get(uid, locale='ru_RU'):
        params = {'locale': locale, 'apikey': config.blizzard_key}
        r = requests.get(url=api['EU']['Character']['Data']['Classes'], params=params)
        if r.status_code != 200:
            if r.status_code == 404:
                raise Exceptions.NotFound(uid, r.json())
            else:
                raise Exceptions.NotOk(r.status_code, r.json())
        else:
            for wow_class in r.json()['classes']:
                if wow_class['id'] == uid:
                    return Class(uid=wow_class['id'], mask=wow_class['mask'], power_type=wow_class['powerType'],
                                 name=wow_class['name'])
            raise Exceptions.NotFound(uid, r.json()['classes'])

    @staticmethod
    def load(locale='ru_RU'):
        params = {'locale': locale, 'apikey': config.blizzard_key}
        r = requests.get(url=api['EU']['Character']['Data']['Classes'], params=params)
        if r.status_code != 200:
            raise Exceptions.NotOk(r.status_code, r.json())
        else:
            class_list = []
            for wow_class in r.json()['classes']:
                class_list.append(Class(uid=wow_class['id'], mask=wow_class['mask'], power_type=wow_class['powerType'],
                                        name=wow_class['name']))
            return class_list

    @staticmethod
    def find(uid):
        for wow_class in classes:
            if wow_class.id == uid:
                return wow_class
        raise Exceptions.NotFound(uid, classes)


realms = Realm.load()
print('Lib-WoW:Loaded {} realms!'.format(len(realms)))
races = Race.load()
print('Lib-WoW:Loaded {} races!'.format(len(races)))
classes = Class.load()
print('Lib-WoW:Loaded {} classes!'.format(len(classes)))

print('Lib-WoW:Ready')
