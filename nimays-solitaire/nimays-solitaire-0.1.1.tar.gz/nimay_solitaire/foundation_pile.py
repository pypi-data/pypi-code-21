from nimay_solitaire.card import Card
from nimay_solitaire.pile import Pile


class FoundationPile(Pile):
    """
    A class that implements a Foundation pile. The four objective piles in Solitaire are Foundation piles.
    """

    def __init__(self, suit):
        super().__init__()
        self.suit = suit

    """
    Check if adding a card to the pile is a valid move in solitaire.
    :param card_to_add: The card to check validity with.
    :return True if adding the card to the pile is a valid move, False otherwise
    """
    def check_valid(self, card_to_add):
        if not card_to_add:
            return False
        if self.cards:
            top_card = self.cards[-1]
            valid_rank = top_card.rank == card_to_add.rank - 1
        else:
            valid_rank = card_to_add.rank == 0
        valid_suit = self.suit == card_to_add.suit
        return valid_rank and valid_suit

    """
    Adds a card to the "top" of the pile.
    :param card: The card to add to the pile
    :param make_visible: boolean to determine whether the card should be visible to the user
    :param check: boolean which should be true to check for validity of the add move
    :returns True if the card was successfully added, False otherwise
    """
    def add_card(self, card, make_visible, check):
        if check and not self.check_valid(card):
            return False
        if make_visible:
            card.visible = True
        self.cards.append(card)
        return True

    """
    Returns a string representation of this foundation pile
    """
    def __str__(self):
        foundation_str = Card.suits[self.suit] + ": "
        foundation_str += str(self.cards[-1]) if self.cards else "Empty"
        return foundation_str
