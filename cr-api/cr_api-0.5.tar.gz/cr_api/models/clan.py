"""
Clan
"""
from .base import BaseModel
from .core import Badge, Region, Arena


class ClanChest(BaseModel):
    def _update_attributes(self, data):
        # crowns
        self.crowns = self._get_attribute(data, 'clanChestCrowns')

        # crown percent
        self.crowns_percent = self._get_attribute(data, 'clanChestCrownsPercent')

        # crowns required
        self.crowns_required = self._get_attribute(data, 'clanChestCrownsRequired')


class ClanMember(BaseModel):
    """Member model in clan."""

    def _update_attributes(self, data):
        # - name
        self.name = self._get_attribute(data, 'name')

        # - arena
        self.arena = Arena(data=self._get_attribute(data, 'arena'))

        # - experience level
        self.experience_level = self._get_attribute(data, 'expLevel')

        # - trophies
        self.trophies = self._get_attribute(data, 'trophies')

        # - score: alias to trophies
        self.score = self._get_attribute(data, 'score')

        # - donations for the week
        self.donations = self._get_attribute(data, 'donations')

        # - current rank
        self.current_rank = self._get_attribute(data, 'currentRank')

        # - previous rank
        self.previous_rank = self._get_attribute(data, 'previousRank')

        # - clan chest crowns
        self.clan_chestcrowns = self._get_attribute(data, 'clanChestCrowns')

        # - player tag
        self.tag = self._get_attribute(data, 'tag')

        # - role: enum
        self.role = self._get_attribute(data, 'role')

        # - role name
        self.role_name = self._get_attribute(data, 'role_name')

        # - clan name
        self.clan_name = self._get_attribute(data, 'clan_name')

        # - clan name
        self.clan_tag = self._get_attribute(data, 'clan_tag')

    @property
    def rank_delta(self):
        """Difference in rank.

        Return None if previous rank is 0
        """
        if self.previous_rank == 0:
            return None
        else:
            return self.current_rank - self.previous_rank

    @property
    def league(self):
        """League ID from Arena ID."""
        return max(0, self.arena.arean_id - 11)

    @property
    def league_icon_url(self):
        """League Icon URL."""
        return (
            'http://smlbiobot.github.io/img/leagues/'
            'league{}.png'
        ).format(self.league)


class Clan(BaseModel):
    """Clash Royale Clan data."""

    def _update_attributes(self, data):
        # - Name of clan
        self.name = self._get_attribute(data, 'name')

        # - badge
        self.badge = Badge(data=self._get_attribute(data, 'badge'))

        # - type of the clan: enum
        self.type = self._get_attribute(data, 'type')

        # - type name
        self.type_name = self._get_attribute(data, 'typeName')

        # - number of memebers in clan
        self.member_count = self._get_attribute(data, 'memberCount')

        # - required trophies to join
        self.required_score = self._get_attribute(data, 'requiredScore')

        # - total donations for the week
        self.donations = self._get_attribute(data, 'donations')

        # - current rank
        # TODO: not sure what this is
        self.current_rank = self._get_attribute(data, 'currentRank')

        # - clan description
        self.description = self._get_attribute(data, 'description')

        # - clan tag
        self.tag = self._get_attribute(data, 'tag')

        # - region
        self.region = Region(data=self._get_attribute(data, 'region'))

        # - members
        members = self._get_attribute(data, 'members')
        clan_dict = {
            "clan_name": self.name,
            "clan_tag": self.tag
        }
        self.members = []
        if members is not None:
            for m in members:
                m.update(clan_dict)
                self.members.append(ClanMember(data=m))

    @property
    def member_tags(self):
        """List of member tags."""
        return [m.tag for m in self.members]
