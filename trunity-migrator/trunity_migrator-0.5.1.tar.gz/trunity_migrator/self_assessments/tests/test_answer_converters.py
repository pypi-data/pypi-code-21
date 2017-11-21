from unittest import TestCase

from trunity_3_client.builders import Answer

from trunity_migrator.self_assessments.answer_converters import convert_multiple_choice


class ConvertersTestCase(TestCase):

    def test_convert_multiple_choice(self):
        t2_question = {
            'question': 'Test Multiple Choice Question',
            'answers': [{
                'correct': 1,
                'feedback': 'Correct!',
                'option': 'Option 1'
            }, {
                'correct': 0,
                'feedback': '',
                'option': 'option 2'
            }, {
                'correct': 0,
                'feedback': '',
                'option': 'option 3'
            }],
            'questionType': 'Multiple Choice'
        }

        t3_expected_answers = [
            Answer('Option 1', True, 1, 'Correct!'),
            Answer('option 2', False, 0),
            Answer('option 3', False, 0),
        ]

        self.assertListEqual(
            convert_multiple_choice(t2_question),
            t3_expected_answers
        )
