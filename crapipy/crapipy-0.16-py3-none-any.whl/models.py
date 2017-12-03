"""
Data models
"""
from box import Box


class BaseModel(Box):
    """
    Base model.
    """

    def __init__(self, *args, **kwargs):
        kwargs.update({
            "camel_killer_box": True,
        })
        super().__init__(*args, **kwargs)


class Clan(BaseModel):
    """Clan."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TopClans(BaseModel):
    """Clan."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Player(BaseModel):
    """Player profile."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def clan_name(self):
        return self.clan.name

    @property
    def clan_role(self):
        return self.clan.role

class TopPlayers(BaseModel):
    """Top Players"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Constants(BaseModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_chest_by_index(self, index):
        """Return chest by index."""
        order = self.chest_cycle.order
        return order[index % len(order)]

    def get_card(self, key=None, card_key=None, name=None):
        """Return card by any property"""
        for card in self.cards:
            if card.key == key:
                return card
            if card.card_key == card_key:
                return card
            if card.name == name:
                return card
        return None


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

    def __str__(self):
        return self._tag

    def __repr__(self):
        return self._tag

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
