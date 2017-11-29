from nimay_solitaire.deck import Deck
from nimay_solitaire.foundation_pile import FoundationPile
from nimay_solitaire.tableau_pile import TableauPile


class Gameboard(object):
    """
    A class that implements the Solitaire gameboard.
    """

    def __init__(self, num_tableau_piles):
        self.num_tableau_piles = num_tableau_piles
        self.deck = Deck()
        self.deck.shuffle()
        self.tableau_piles = [TableauPile() for _ in range(self.num_tableau_piles)]
        self._fill_tableau_piles()
        self.num_foundation_piles = self.deck.MAX_SUIT + 1
        self.foundation_piles = [FoundationPile(i) for i in range(self.num_foundation_piles)]

    """
    Initializes the tableau piles with cards
    """
    def _fill_tableau_piles(self):
        for i in range(self.num_tableau_piles):
            for j in range(0, i+1):
                card = self.deck.draw_card()
                if not card:
                    print("Deck depleted before filling tableau piles")
                    return
                # Last card placed in each iteration should be visible
                card_visible = i == j
                # Do not check for card validity in initial setup
                self.tableau_piles[i].add_card(card, card_visible, False)

    """
    Return a string representation of the board. Useful for printing the state of the board.
    """
    def __str__(self):
        board_str = ""
        board_str += "WASTE:\n"
        if self.deck.waste_pile.cards:
            board_str += str(self.deck.waste_pile.cards[-1])
        else:
            board_str += "Empty"
        board_str += "\n\n"

        board_str += "TABLEAU:\n"
        for i, pile in enumerate(self.tableau_piles):
            board_str += str(i) + ": " + str(pile) + "\n"
        board_str += "\n"

        board_str += "FOUNDATION:\n"
        for pile in self.foundation_piles:
            board_str += str(pile) + "\n"
        return board_str
