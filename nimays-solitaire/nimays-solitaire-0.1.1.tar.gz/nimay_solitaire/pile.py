import random


class Pile(object):
    """
    Base class representation of a pile. All major elements in solitaire are some kind of pile.
    """

    def __init__(self):
        self.cards = []

    """
    Check if adding a card to the pile is a valid move in solitaire. In the case of this basic pile, there are no
    restrictions to adding a card.
    :param card_to_add: The card to check validity with.
    :return True if adding the card to the pile is a valid move, False otherwise
    """
    def check_valid(self, card_to_add):
        return card_to_add is not None

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
    Remove the top card in the pile.
    :return The removed card if a card was removed, None otherwise
    """
    def remove_card(self):
        if not self.cards:
            return None
        top_card = self.cards[-1]
        self.cards = self.cards[:-1]
        return top_card

    """
    Shuffles the cards in the pile.
    """
    def shuffle(self):
        random.shuffle(self.cards)
