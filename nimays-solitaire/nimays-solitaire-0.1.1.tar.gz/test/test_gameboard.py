from unittest import TestCase

from nimay_solitaire.gameboard import Gameboard


class TestGameboard(TestCase):
    """
    A class to test the Gameboard class
    """

    """
    Test gameboard initialization
    """
    def test_init(self):
        gb = Gameboard(7)
        self.assertEqual(7, gb.num_tableau_piles)
        self.assertEqual(7, len(gb.tableau_piles))
        self.assertEqual(4, gb.num_foundation_piles)
        self.assertEqual(4, len(gb.foundation_piles))
        for i in range(7):
            self.assertEqual(i+1, len(gb.tableau_piles[i].cards))
        self.assertEqual(24, len(gb.deck.stock_pile.cards))
