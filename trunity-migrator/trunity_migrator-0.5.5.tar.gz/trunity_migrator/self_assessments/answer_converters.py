"""
Collection of converters that transform T2 answers to list of T3 answer objects.
"""
from typing import List

from trunity_3_client.builders import Answer

# TODO: move this constant to settings
DEFAULT_SCORE = 1


def convert_multiple_choice(t2_question: dict) -> List[Answer]:
    t3_answers = []
    t2_answers = t2_question['answers']

    for t2_answer in t2_answers:
        t3_answers.append(
            Answer(
                text=t2_answer['option'],
                correct=True if t2_answer['correct'] == 1 else False,
                score=DEFAULT_SCORE if t2_answer['correct'] == 1 else 0,
                feedback=t2_answer['feedback']
            ))

    return t3_answers
