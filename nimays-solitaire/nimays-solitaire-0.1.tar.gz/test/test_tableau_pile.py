from unittest import TestCase

from nimay_solitaire.card import Card
from nimay_solitaire.tableau_pile import TableauPile


class TestTableauPile(TestCase):
    """
    A class for test the TableauPile class
    """

    """
    Test initialization of a foundation pile
    """
    def test_init(self):
        fp = TableauPile()
        self.assertEqual(0, len(fp.cards))

    """
    Test checking validity of a valid card
    """
    def test_check_valid(self):
        fp = TableauPile()
        red_king_card = Card(Card.HEART, 12, False)
        self.assertTrue(fp.check_valid(red_king_card))
        fp.add_card(red_king_card, False, True)
        black_queen_card = Card(Card.CLUB, 11, False)
        self.assertTrue(fp.check_valid(black_queen_card))

    """
    Test checking validity of a invalid card
    """
    def test_check_valid_invalid_case(self):
        fp = TableauPile()
        red_king_card = Card(Card.HEART, 12, False)
        self.assertTrue(fp.check_valid(red_king_card))
        fp.add_card(red_king_card, False, True)
        red_queen_card = Card(Card.DIAMOND, 11, False)
        self.assertFalse(fp.check_valid(red_queen_card))

    """
    Test adding valid cards to the foundation pile
    """
    def test_add_card(self):
        fp = TableauPile()
        red_king_card = Card(Card.HEART, 12, False)
        self.assertTrue(fp.add_card(red_king_card, False, True))
        self.assertEqual(1, len(fp.cards))
        black_queen_card = Card(Card.CLUB, 11, False)
        self.assertTrue(fp.add_card(black_queen_card, False, True))
        self.assertEqual(2, len(fp.cards))

    """
    Test adding an invalid card to the foundation pile
    """
    def test_add_card_invalid_case(self):
        fp = TableauPile()
        red_non_king_card = Card(Card.HEART, 0, False)
        self.assertFalse(fp.add_card(red_non_king_card, False, True))
        self.assertEqual(0, len(fp.cards))

    """
    Test removing a card from the tableau pile
    """
    def test_remove_card(self):
        fp = TableauPile()
        red_king_card = Card(Card.HEART, 12, False)
        black_queen_card = Card(Card.CLUB, 11, False)
        red_jack_card = Card(Card.DIAMOND, 10, False)
        fp.add_card(red_king_card, False, True)
        fp.add_card(black_queen_card, False, True)
        fp.add_card(red_jack_card, True, True)
        cards = fp.remove_card(1)
        self.assertEqual(black_queen_card, cards[0])
        self.assertEqual(red_jack_card, cards[1])

