import pytest

from cr_api import Client


@pytest.mark.asyncio
async def test_constants():
    client = Client()
    constants = await client.get_constants()
    assert constants.arenas[0].arena == 'Arena 1'
    assert constants.badges["16000000"] == 'Flame_01'
    assert constants.chest_cycle.order[0] == 'Silver'
    assert constants.get_chest_by_index(3) == 'Gold'
    assert constants.get_region_named("Europe").is_country == False
    assert constants.get_region_named("Swaziland").is_country == True
