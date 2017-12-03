import pytest

from crapipy import AsyncClient, Client


@pytest.mark.asyncio
async def test_top_players_async():
    client = AsyncClient()
    top_players = await client.get_top_players()
    print(top_players)
    assert top_players.last_updated > 0
    assert len(top_players.players) > 0
    assert top_players.players[0].clan.name


def test_top_players():
    client = Client()
    top_players = client.get_top_players()
    print(top_players)
    assert top_players.last_updated > 0
    assert len(top_players.players) > 0
    assert top_players.players[0].clan.name
