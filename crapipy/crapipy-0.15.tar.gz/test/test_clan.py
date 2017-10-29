import pytest

from crapipy import AsyncClient, Client, APIError


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

@pytest.mark.asyncio
async def test_invalid_clan_async():
    client = AsyncClient()
    with pytest.raises(APIError):
        clan = await client.get_clan('123445')

def test_invalid_clan():
    client = Client()
    with pytest.raises(APIError):
        clan = client.get_clan('123445')


