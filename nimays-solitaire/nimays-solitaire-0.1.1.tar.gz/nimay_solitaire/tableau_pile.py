from nimay_solitaire.card import Card
from nimay_solitaire.pile import Pile


class TableauPile(Pile):
    """
    This class implements a Tableau pile, which is are the seven piles that make up the main table in Solitaire.
    """

    def __init__(self):
        super().__init__()

    """
    Check if adding a card to the pile is a valid move in solitaire.
    :param card_to_add: The card to check validity with.
    :return True if adding the card to the pile is a valid move, False otherwise
    """
    def check_valid(self, card_to_add):
        if not self.cards:
            return card_to_add.rank == Card.KING
        top_card = self.cards[-1]
        valid_rank = top_card.rank == card_to_add.rank + 1
        valid_color = not card_to_add.same_color(top_card)
        return valid_rank and valid_color

    """
    Remove a card and all cards "above" it in the pile.
    :param index: The index in the pile of the card to remove
    :return An ordered list of cards including the removed cards and all cards above it in the pile
    """
    def remove_card(self, index):
        if index >= len(self.cards) or index < 0:
            return []
        removed_pile = self.cards[index:]
        self.cards = self.cards[:index]
        if self.cards:
            self.cards[index-1].visible = True
        return removed_pile

    """
    For adding visible cards from one tableau pile to another.
    :param cards: cards to add to this tableau pile
    :return True if all cards were added successfully, false otherwise
    """
    def add_cards(self, cards):
        success = True
        for card in cards:
            success = self.add_card(card, True, True)
            if not success:
                break
        return success

    """
    Returns a string representation of the tableau pile
    """
    def __str__(self):
        tableau_str = ""
        num_invisible = len([card for card in self.cards if not card.visible])
        if num_invisible:
            tableau_str += "(%s) face down" % num_invisible
        for card in self.cards:
            if card.visible:
                if tableau_str:
                    tableau_str += ", "
                tableau_str += str(card)
        return tableau_str
