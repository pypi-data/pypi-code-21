from unittest import TestCase

from nimay_solitaire.card import Card
from nimay_solitaire.pile import Pile


class TestPile(TestCase):
    """
    Class for testing the Pile Class
    """

    """
    Test pile initialization
    """
    def test_init(self):
        pile = Pile()
        self.assertEqual(0, len(pile.cards))

    """
    Test pile validation check with valid card
    """
    def test_check_valid_positive_case(self):
        pile = Pile()
        card = Card(Card.HEART, 0, False)
        self.assertTrue(pile.check_valid(card))

    """
    Test pile validation check with None card
    """
    def test_check_valid_none(self):
        pile = Pile()
        self.assertFalse(None)

    """
    Test adding a valid card to the pile
    """
    def test_add_card_valid(self):
        pile = Pile()
        card = Card(Card.HEART, 0, False)
        self.assertTrue(pile.add_card(card, False, True))
        self.assertEqual(1, len(pile.cards))

    """
    Test adding an invalid card to the pile
    """
    def test_add_card_invalid(self):
        pile = Pile()
        self.assertFalse(pile.add_card(None, False, True))
        self.assertEqual(0, len(pile.cards))

    """
    Test removing a card from a non-empty pile
    """
    def test_remove_card(self):
        pile = Pile()
        card = Card(Card.HEART, 0, False)
        pile.add_card(card, False, True)
        result = pile.remove_card()
        self.assertEqual(card, result)
        self.assertEqual(0, len(pile.cards))

    """
    Test removing a card from an empty pile
    """
    def test_remove_card_empty(self):
        pile = Pile()
        result = pile.remove_card()
        self.assertEqual(None, result)

    """
    Test shuffling the pile
    """
    def test_shuffle(self):
        pile = Pile()
        for i in range(13):
            card = Card(Card.HEART, i, False)
            pile.add_card(card, False, True)
        pile.shuffle()
        all_equal = True
        for i in range(13):
            all_equal = i == pile.cards[i].rank
            if not all_equal:
                break
        self.assertFalse(all_equal)
