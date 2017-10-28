import pytest

from cr_api import AsyncClient, Client


@pytest.mark.asyncio
async def test_clan_async():
    client = AsyncClient()
    clan = await client.get_clan('2CCCP')
    assert clan.name == 'Reddit Alpha'
    assert clan.badge.key == 'A_Char_Rocket_02'

def test_clan():
    client = Client()
    clan = client.get_clan('2CCCP')
    assert clan.name == 'Reddit Alpha'
    assert clan.badge.key == 'A_Char_Rocket_02'


