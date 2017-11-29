from unittest import TestCase

from nimay_solitaire.card import Card
from nimay_solitaire.foundation_pile import FoundationPile


class TestFoundationPile(TestCase):
    """
    A class to test the foundation pile.
    """

    """
    Test the foundation pile initialization
    """
    def test_init(self):
        fp = FoundationPile(Card.HEART)
        self.assertEqual(0, len(fp.cards))
        self.assertEqual(Card.HEART, fp.suit)

    """
    Test the foundation validity check on a valid case
    """
    def test_check_valid(self):
        fp = FoundationPile(Card.HEART)
        card = Card(Card.HEART, 0, True)
        self.assertTrue(fp.check_valid(card))
        fp.add_card(card, True, True)
        card2 = Card(Card.HEART, 1, True)
        self.assertTrue(fp.check_valid(card2))

    """
    Test the foundation validity check on a invalid case
    """
    def test_check_valid_invalid_case(self):
        fp = FoundationPile(Card.HEART)
        self.assertFalse(fp.check_valid(None))

    """
    Test adding a valid card to the foundation pile
    """
    def test_add_card(self):
        fp = FoundationPile(Card.HEART)
        card = Card(Card.HEART, 0, False)
        self.assertTrue(fp.add_card(card, True, True))
        self.assertEqual(1, len(fp.cards))

    """
    Test adding a invalid card to the foundation pile
    """
    def test_add_card_invalid_case(self):
        fp = FoundationPile(Card.HEART)
        self.assertFalse(fp.add_card(None, True, True))
        self.assertEqual(0, len(fp.cards))

