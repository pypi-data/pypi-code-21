from crapipy import Client

client = Client()
top_players = client.get_top_players()
print(top_players)
print(top_players.last_updated)
print(top_players.players)
print(top_players.players[0].clan.name)
print(top_players.players[0].trophies)