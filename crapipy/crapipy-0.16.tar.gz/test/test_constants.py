import pytest

from crapipy import AsyncClient
import pprint


@pytest.mark.asyncio
async def test_constants():
    client = AsyncClient()
    constants = await client.get_constants()
    pp = pprint.PrettyPrinter(indent=4)
    assert constants.arenas[0].arena == 'Arena 1'
    assert constants.badges["16000000"] == 'Flame_01'
    assert constants.chest_cycle.order[0] == 'Silver'
    assert constants.get_chest_by_index(3) == 'Gold'

    archers = constants.get_card(key='archers')
    assert archers.elixir == 3
    assert archers.name == 'Archers'
    assert archers.rarity == 'Common'

    # assert constants.get_region_named("Europe").is_country == False
    # assert constants.get_region_named("Swaziland").is_country == True


