import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import steam_api

# Debug use only
STEAM_WEB_API_KEY = '079FDD108A5659AEEC5D544D18B2605B'
STEAM_WEB_API_DOMAIN = 'leixr.com'

user = steam_api.user.User(STEAM_WEB_API_KEY, '76561197960435530')

print(user.steam_id)

print(user.profiles)

print(user.friends('all'))

print(user.game_achievements(440))

print(user.game_stats(440))

print(user.owned_games())

print(user.recently_played_games())
