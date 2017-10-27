"""
Player profile
"""

from .base import BaseModel
from .core import Deck, Badge, Arena



class PlayerClan(BaseModel):
    """Clan model inside a profile."""

    def _update_attributes(self, data):
        self.tag = self._get_attribute(data, 'tag')
        self.name = self._get_attribute(data, 'name', 'No Clan')
        self.role = self._get_attribute(data, 'role', 'N/A')
        self.badge = Badge(data=self._get_attribute(data, 'badge'))



class PlayerExperience(BaseModel):
    """Player experience."""

    def _update_attributes(self, data):
        self.level = self._get_attribute(data, 'level')
        self.xp = self._get_attribute(data, 'xp')
        self.xp_required_for_level_up = self._get_attribute(data, 'xpRequiredForLevelUp')
        self.xp_to_level_up = self._get_attribute(data, 'xpToLevelUp')


class PlayerStats(BaseModel):
    """Player stats."""

    def _update_attributes(self, data):
        self.legendary_trophies = self._get_attribute(data, 'legendaryTrophies')
        self.tournament_cards_won = self._get_attribute(data, 'tournamentCardsWon')
        self.max_trophies = self._get_attribute(data, 'maxTrophies')
        self.three_crown_wins = self._get_attribute(data, 'threeCrownWins')
        self.cards_found = self._get_attribute(data, 'cardsFound')
        self.favorite_card = self._get_attribute(data, 'favoriteCard')
        self.total_donatons = self._get_attribute(data, 'totalDonations')
        self.challenge_max_wins = self._get_attribute(data, 'challengeMaxWins')
        self.challenge_cards_won = self._get_attribute(data, 'challengeCardsWon')
        self.level = self._get_attribute(data, 'level')


class PlayerGames(BaseModel):
    """Player game stats."""

    def _update_attributes(self, data):
        self.total = self._get_attribute(data, 'total')
        self.tournament_games = self._get_attribute(data, 'tournamentGames')
        self.wins = self._get_attribute(data, 'wins')
        self.losses = self._get_attribute(data, 'losses')
        self.draws = self._get_attribute(data, 'draws')
        self.current_win_streak = self._get_attribute(data, 'currentWinStreak')


class PlayerChestCycle(BaseModel):
    """Player chest cycle"""

    def _update_attributes(self, data):
        self.position = self._get_attribute(data, 'position')
        self.super_magical_pos = self._get_attribute(data, 'superMagicalPos')
        self.legendary_pos = self._get_attribute(data, 'legendaryPos')
        self.epic_pos = self._get_attribute(data, 'epicPos')


class PlayerShopOffers(BaseModel):
    """Shop offers."""

    def _update_attributes(self, data):
        self.legendary = self._get_attribute(data, 'legendary')
        self.epic = self._get_attribute(data, 'epic')
        self.arena = self._get_attribute(data, 'arena')


class Player(BaseModel):
    """A player profile in Clash Royale."""

    def _update_attributes(self, data):
        #: Unique player tag.
        self.tag = self._get_attribute(data, 'tag')

        #: In-game name, aka username
        self.name = self._get_attribute(data, 'name')

        #: Current trophies
        self.trophies = self._get_attribute(data, 'trophies')

        #: name change option
        self.name_changed = self._get_attribute(data, 'nameChanged')

        #: global rank
        self.global_rank = self._get_attribute(data, 'globalRank')

        #: ----------
        #: Clan
        # self.clan = self._get_attribute(player, 'clan')
        self.clan = PlayerClan(data=self._get_attribute(data, 'clan'))

        #: Not in clan
        self.not_in_clan = self.clan is None

        #: Clan name
        self.clan_name = 'No Clan'

        #: Clan tag
        self.clan_tag = None

        #: Clan role
        self.clan_role = 'N/A'

        self.clan_name = self.clan.name
        self.clan_tag = self.clan.tag
        self.clan_role = self.clan.role

        self.badge = Badge(data=self._get_attribute(data, 'badge'))

        #: Arena
        self.arena = Arena(data=self._get_attribute(data, 'arena'))

        #: Experience
        self.experience = PlayerExperience(data=self._get_attribute(data, 'experience'))

        #: Stats
        self.stats = PlayerStats(data=self._get_attribute(data, 'stats'))

        #: Games
        self.games = PlayerGames(data=self._get_attribute(data, 'games'))

        #: Chests
        self.chest_cycle = PlayerChestCycle(data=self._get_attribute(data, 'chestCycle'))

        #: Shop offers
        self.shop_offers = PlayerShopOffers(data=self._get_attribute(data, 'shopOffers'))

        #: Deck
        self.deck = Deck(data=self._get_attribute(data, 'currentDeck'))
