import pytest

from cr_api import Client


@pytest.mark.asyncio
async def test_clan():
    client = Client()
    clan = await client.get_clan('2CCCP')
    assert clan.name == 'Reddit Alpha'
    assert clan.badge.key == 'A_Char_Rocket_02'


