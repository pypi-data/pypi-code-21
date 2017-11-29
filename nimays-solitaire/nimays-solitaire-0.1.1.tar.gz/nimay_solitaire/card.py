
class Card(object):
    """
    A class that represents a typical 4-suit, 2-color, 13-rank playing card.
    """

    # Suit name aliases
    HEART = 0
    DIAMOND = 1
    CLUB = 2
    SPADE = 3

    # Card name aliases
    ACE = 0
    JACK = 10
    QUEEN = 11
    KING = 12

    suits = ["heart", "diamond", "club", "spade"]
    red_suits = {HEART, DIAMOND}
    black_suits = {CLUB, SPADE}
    ranks = ["ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king"]

    """
    :param suit: An integer from 0-3
    :param rank: An integer from 0-12
    :param visible: A boolean
    """
    def __init__(self, suit, rank, visible):
        self.suit = suit
        self.rank = rank
        self.visible = visible

    """
    Checks if the two cards have the same color.
    :param other: The card to compare colors with.
    :return True if the cards have the same color, False otherwise
    """
    def same_color(self, other):
        return (self.suit in self.red_suits and other.suit in self.red_suits) or\
               (self.suit in self.black_suits and other.suit in self.black_suits)

    """
    Get the string representation of a card.
    """
    def __str__(self):
        return "%s of %ss" % (self.ranks[self.rank], self.suits[self.suit])

    """
    Two cards are equal if they have the same suit and rank
    """
    def __eq__(self, other):
        return self.suit == other.suit and self.rank == other.rank
