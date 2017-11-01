import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import steam_api

achievements = steam_api.user_stats.GameUserStats(440)
print(achievements.game_id)
print(achievements.achievements)

achievements.game_id = 400
print(achievements.game_id)
print(achievements.achievements)

# not existed game id
achievements.game_id = 401
print(achievements.game_id)
print(achievements.achievements)