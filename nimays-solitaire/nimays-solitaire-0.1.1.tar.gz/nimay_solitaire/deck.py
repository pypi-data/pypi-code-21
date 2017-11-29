from nimay_solitaire.card import Card
from nimay_solitaire.pile import Pile


class Deck(object):
    """
    A pile that represents a standard deck of 52 cards.
    """

    # Correspond to the maximum suit/rank of the cards used in this deck
    MAX_SUIT = 3
    MAX_RANK = 12

    def __init__(self):
        self.stock_pile = Pile()
        self.waste_pile = Pile()
        self._fill_deck()

    """
    Populate the deck with the standard 52 cards. Used for initializing the deck.
    """
    def _fill_deck(self):
        for suit in range(self.MAX_SUIT + 1):
            for rank in range(self.MAX_RANK + 1):
                self.stock_pile.add_card(Card(suit, rank, False), False, True)

    """
    Shuffle the positions of the non-waste cards in the deck.
    """
    def shuffle(self):
        self.stock_pile.shuffle()

    """
    Transfer cards from waste pile back into stock pile.
    :return True if at least one card was added successfully to the stock pile, False otherwise
    """
    def add_cards_from_waste(self):
        added = False
        card = self.waste_pile.remove_card()
        while card:
            if self.stock_pile.add_card(card, False, True):
                added = True
            card = self.waste_pile.remove_card()
        return added

    """
    Remove the top card in the pile.
    :return The removed card if a card was removed, None otherwise
    """
    def draw_card(self):
        return self.stock_pile.remove_card()

    """
    Draws a card from the stock pile and places it into the waste pile. If the stock pile is empty, refill it with cards
    from the waste file and then try to draw a card again
    :return True if the operation was successful, False otherwise
    """
    def draw_card_to_waste(self):
        card = self.draw_card()
        if card:
            return self.waste_pile.add_card(card, True, True)
        else:
            if self.add_cards_from_waste():
                return self.draw_card_to_waste()
        return False
