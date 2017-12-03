import pytest

from crapipy import AsyncClient, Client


def assert_player_model(player):
    assert player.name == 'SML'
    assert player.tag == 'C0G20PR2'
    assert player.clan.name == 'Reddit Delta'
    assert player.clan.role == 'Leader'
    assert player.clan_name == player.clan.name
    assert player.clan_role == player.clan.role
    assert player.current_deck is not None
    assert player.shop_offers is not None
    assert player.arena.arena_id == player.arena.arenaID
    assert player.arena.arena_id is not None


@pytest.mark.asyncio
async def test_profile_async():
    client = AsyncClient()
    player = await client.get_profile('C0G20PR2')
    assert_player_model(player)


def test_profile():
    client = Client()
    player = client.get_profile('C0G20PR2')
    assert_player_model(player)


@pytest.mark.asyncio
async def test_profile_equal():
    client = AsyncClient()
    player1 = await client.get_profile('C0G20PR2')
    player2 = await client.get_profile('C0G20PR2')
    assert player1 == player2


@pytest.mark.asyncio
async def test_profile_not_equal():
    client = AsyncClient()
    player1 = await client.get_profile('C0G20PR2')
    player2 = await client.get_profile('PY9VC98C')
    assert player1 != player2
