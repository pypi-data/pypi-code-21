from unittest import TestCase

from nimay_solitaire.card import Card


class TestCard(TestCase):
    """
    A class for testing the Card class
    """

    """
    Tests whether the same color function can recognized the cards of the same color
    """
    def test_same_color(self):
        heart_card = Card(Card.HEART, 0, False)
        diamond_card = Card(Card.DIAMOND, 0, False)
        self.assertTrue(heart_card.same_color(diamond_card))
        club_card = Card(Card.CLUB, 0, False)
        spade_card = Card(Card.SPADE, 0, False)
        self.assertTrue(club_card.same_color(spade_card))

    """
    Tests whether the same color function can recognized the cards of the different color
    """
    def test_same_color_different(self):
        heart_card = Card(Card.HEART, 0, False)
        diamond_card = Card(Card.DIAMOND, 0, False)
        club_card = Card(Card.CLUB, 0, False)
        spade_card = Card(Card.SPADE, 0, False)
        self.assertFalse(club_card.same_color(heart_card))
        self.assertFalse(club_card.same_color(diamond_card))
        self.assertFalse(spade_card.same_color(heart_card))
        self.assertFalse(spade_card.same_color(diamond_card))

    """
    Tests whether the getting the string representation of a card works as expected
    """
    def test_str(self):
        card = Card(Card.HEART, 0, False)
        self.assertEqual("ace of hearts", str(card))

    """
    Tests whether the card equality override works
    """
    def test_eq(self):
        card1 = Card(Card.HEART, 0, False)
        card2 = Card(Card.HEART, 0, True)
        self.assertTrue(card1 == card2)
        card3 = Card(Card.SPADE, 1, False)
        self.assertFalse(card1 == card3)
        self.assertFalse(card2 == card3)

