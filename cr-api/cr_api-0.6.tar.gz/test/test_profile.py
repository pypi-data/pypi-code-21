import pytest

from cr_api import Client
from cr_api.models import Player


@pytest.mark.asyncio
async def test_profile():
    client = Client()
    player = await client.get_profile('C0G20PR2')
    assert player.name == 'SML'
    assert player.tag == 'C0G20PR2'
    assert player.clan_name == 'Reddit Delta'
    assert player.clan_role == 'Leader'
    assert player.deck is not None
    assert player.shop_offers is not None


@pytest.mark.asyncio
async def test_profile_equal():
    client = Client()
    player1 = await client.get_profile('C0G20PR2')
    player2 = await client.get_profile('C0G20PR2')
    assert player1 == player2


@pytest.mark.asyncio
async def test_profile_not_equal():
    client = Client()
    player1 = await client.get_profile('C0G20PR2')
    player2 = await client.get_profile('PY9VC98C')
    assert player1 != player2

def test_profile_model():
    """Load static data to test model."""
    with open('./test/data/C0G20PR2.json') as f:
        json_str = f.read()

    p = Player.from_json(json_str)
    assert p.name == 'SML'
    assert p.tag == 'C0G20PR2'
    assert p.clan_name == 'Reddit Delta'
    assert p.clan_role == 'Leader'
    assert p.arena is not None
    assert p.arena.image_url == '/arena/league2.png'
    assert p.arena.arena_id == 13
    assert p.arena.name == 'Challenger II'
    assert p.clan.name == 'Reddit Delta'
    assert p.clan.badge.key == 'A_Char_Rocket_02'
    assert p.experience.level == 12