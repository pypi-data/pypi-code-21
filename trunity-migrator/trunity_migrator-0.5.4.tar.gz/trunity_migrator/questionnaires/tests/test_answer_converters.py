from unittest import TestCase

from trunity_3_client.builders import Answer, NumericAnswer, TrueFalseAnswer

from trunity_migrator.questionnaires.answer_converters import (
    convert_multiple_choice,
    convert_multiple_answer,
    convert_true_false,
    convert_short_answer,
)


class ConvertersTestCase(TestCase):

    def test_convert_multiple_choice(self):
        t2_question = {
            'type': 'multipleChoice',
            'feedback': '',
            'answers': ['foo', 'bar', 'baz'],
            'correct': '0',
            'question': '<p>This is a Multiple Choice</p>\n',
            'questionId': 'qceacacd180549eb663a3f3b8b75fdf4f'
        }

        t3_expected_answers = [
            Answer('foo', True, 1),
            Answer('bar', False, 0),
            Answer('baz', False, 0),
        ]

        self.assertListEqual(
            convert_multiple_choice(t2_question),
            t3_expected_answers
        )

    def test_convert_multiple_answer(self):
        t2_question = {
            'type': 'multipleAnswer',
            'feedback': '',
            'answers': ['foo', 'bar', 'baz'],
            'correct': ['0', '1'],
            'question': '<p>This is Multiple Answer</p>\n',
            'questionId': 'qe7c13ce3d94a37e84669953d44425ab1'
        }

        t3_expected_answers = [
            Answer('foo', True, 1),
            Answer('bar', True, 1),
            Answer('baz', False, 0),
        ]

        self.assertListEqual(
            convert_multiple_answer(t2_question),
            t3_expected_answers
        )

    def test_convert_multiple_answer_2(self):
        """
        Additional test to fix a bug mentioned by Sam.

        Due to that bug we cannot migrate sites like this: http://www.trunity.net/qp-test-ma-1/
        """
        t2_question = {
            'feedback': '',
            'type': 'multipleAnswer',
            'questionId': 'q17e4827351f08caf98112222aae2b9c7',
            'answers': ['Incorrect', 'Correct', 'Correct', 'Incorrect', 'Correct', 'Incorrect'],
            'correct': ['1', '2', '4']
        }

        t3_expected_answers = [
            Answer('Incorrect', False, 0),
            Answer('Correct', True, 1),
            Answer('Correct', True, 1),
            Answer('Incorrect', False, 0),
            Answer('Correct', True, 1),
            Answer('Incorrect', False, 0),
        ]

        self.assertListEqual(
            convert_multiple_answer(t2_question),
            t3_expected_answers
        )

    def test_convert_true_false(self):
        t2_question = {
            'type': 'trueFalse',
            'question': '<p>This is TrueFalse</p>\n',
            'feedback': '',
            'correct': 'true',
            'questionId': 'q029c06026471ad680217745405038d5d'
        }

        t3_expected_answers = [
            TrueFalseAnswer(True, True, 1),
            TrueFalseAnswer(False, False, 0),
        ]

        self.assertListEqual(
            convert_true_false(t2_question),
            t3_expected_answers
        )

    def test_convert_short_answer(self):
        t2_question = {
            'type': 'shortAnswer',
            'question': '<p>This is Short Answer</p>\n',
            'answers': ['foo', 'bar', '42'],
            'feedback': '',
            'questionId': 'qe5dc29499b1664e1581c240379fd3101'
        }

        t3_expected_answers = [
            Answer('foo', True, 1),
            Answer('bar', True, 1),
            Answer('42', True, 1),
        ]

        self.assertListEqual(
            convert_short_answer(t2_question),
            t3_expected_answers
        )

