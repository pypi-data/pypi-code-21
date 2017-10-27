"""
Core models. Shared by multiple models.
"""
from .base import BaseModel


class Card(BaseModel):
    """Card."""

    def _update_attributes(self, data):
        self.name = self._get_attribute(data, 'name')
        self.rarity = self._get_attribute(data, 'rarity')
        self.level = self._get_attribute(data, 'level')
        self.count = self._get_attribute(data, 'count')
        self.required_for_upgrade = self._get_attribute(data, 'requiredForUpgrade')
        self.card_id = self._get_attribute(data, 'card_id')
        self.key = self._get_attribute(data, 'key')
        self.card_key = self._get_attribute(data, 'card_key')
        self.elixir = self._get_attribute(data, 'elixir')
        self.type = self._get_attribute(data, 'type')
        self.arena = self._get_attribute(data, 'arena')
        self.description = self._get_attribute(data, 'description')
        self.decklink = self._get_attribute(data, 'decklink')
        self.left_to_upgrade = self._get_attribute(data, 'leftToUpgrade')


class Deck(BaseModel):
    """Deck with cards."""

    def _update_attributes(self, data):
        self.cards = [Card(data=c) for c in data]


class Badge(BaseModel):
    def _update_attributes(self, data):
        # - url
        self.url = self._get_attribute(data, 'url', 'http://smlbiobot.github.io/img/emblems/NoClan.png')

        # - filename
        self.filename = self._get_attribute(data, 'filename')

        # - key
        self.key = self._get_attribute(data, 'key')


class Region(BaseModel):
    def _update_attributes(self, data):
        # - region is a country
        is_country = self._get_attribute(data, 'isCountry')
        self.is_country = is_country == True or is_country == 'true'

        # - name
        self.name = self._get_attribute(data, 'name')


class Arena(BaseModel):
    def _update_attributes(self, data):
        self.image_url = self._get_attribute(data, 'imageURL')
        self.arena = self._get_attribute(data, 'arena')
        self.arena_id = self._get_attribute(data, 'arenaID')
        self.name = self._get_attribute(data, 'name')
        self.trophy_limit = self._get_attribute(data, 'trophyLimit')

class Rarity(BaseModel):
    """Rarity."""
    def _update_attributes(self, data):
        self.balance_multiplier = self._get_attribute(data, 'balance_multiplier')
        self.chance_weight = self._get_attribute(data, 'chance_weight')
        self.clone_relative_level = self._get_attribute(data, 'clone_relative_level')
        self.donate_capacity = self._get_attribute(data, 'donate_capacity')
        self.donate_reward = self._get_attribute(data, 'donate_reward')
        self.donate_xp = self._get_attribute(data, 'donate_xp')
        self.mirror_relative_level = self._get_attribute(data, 'mirror_relative_level')
        self.name = self._get_attribute(data, 'name')
        self.power_level_multiplier = self._get_attribute(data, 'power_level_multiplier')
        self.refund_gems = self._get_attribute(data, 'refund_gems')
        self.relative_level = self._get_attribute(data, 'relative_level')
        self.sort_capacity = self._get_attribute(data, 'sort_capacity')
        self.upgrade_cost = self._get_attribute(data, 'upgrade_cost')
        self.upgrade_exp = self._get_attribute(data, 'upgrade_exp')
        self.upgrade_material_count = self._get_attribute(data, 'upgrade_material_count')

class ChestCycle(BaseModel):
    """Chest cycle."""
    def _update_attributes(self, data):
        self.order = self._get_attribute(data, 'order')
        
        
        
class Tag:
    """SuperCell tags."""

    TAG_CHARACTERS = "0289PYLQGRJCUV"

    def __init__(self, tag: str):
        """Init.

        Remove # if found.
        Convert to uppercase.
        Convert Os to 0s if found.
        """
        if tag.startswith('#'):
            tag = tag[1:]
        tag = tag.replace('O', '0')
        tag = tag.upper()
        self._tag = tag

    @property
    def tag(self):
        """Return tag as str."""
        return self._tag

    @property
    def valid(self):
        """Return true if tag is valid."""
        for c in self.tag:
            if c not in self.TAG_CHARACTERS:
                return False
        return True

    @property
    def invalid_chars(self):
        """Return list of invalid characters."""
        invalids = []
        for c in self.tag:
            if c not in self.TAG_CHARACTERS:
                invalids.append(c)
        return invalids

    @property
    def invalid_error_msg(self):
        """Error message to show if invalid."""
        return (
            'The tag you have entered is not valid. \n'
            'List of invalid characters in your tag: {}\n'
            'List of valid characters for tags: {}'.format(
                ', '.join(self.invalid_chars),
                ', '.join(self.TAG_CHARACTERS)
            ))
