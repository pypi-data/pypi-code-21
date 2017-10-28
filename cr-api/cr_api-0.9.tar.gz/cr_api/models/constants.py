from .base import BaseModel
from .core import Region, Badge, Arena, Rarity, Card, ChestCycle

class Constants(BaseModel):
    """API contants."""
    def _update_attributes(self, data):
        self.arenas = [Arena(data=d) for d in self._get_attribute(data, "arenas")]
        self.badges = self._get_attribute(data, "badges")
        self.chest_cycle = ChestCycle(data=self._get_attribute(data, "chestCycle"))
        self.regions = [Region(data=d) for d in self._get_attribute(data, "countryCodes")]
        self.country_codes = self.regions
        self.rarities = [Rarity(data=d) for d in self._get_attribute(data, "rarities")]
        self.cards = [Card(data=d) for d in self._get_attribute(data, "cards")]

    def get_region_named(self, name):
        """Return region by name."""
        for region in self.regions:
            if region.name == name:
                return region
        return None

    def get_chest_by_index(self, index):
        """Return chest by index."""
        return self.chest_cycle.order[index]

