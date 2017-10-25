import pytest

from cr_api import Client


@pytest.mark.asyncio
async def test_profiles():
    client = Client()
    players = await client.get_profiles(['C0G20PR2', 'PY9VC98C'])
    assert players[0].name == 'SML'
    assert players[0].tag == 'C0G20PR2'
    assert players[0].clan_name == 'Reddit Delta'
    assert players[0].clan_role == 'Leader'
    assert players[1].name == 'Selfish'
    assert players[1].tag == 'PY9VC98C'
    assert players[1].clan_name == 'Reddit Gents.'
    assert players[1].clan_role == 'Leader'
