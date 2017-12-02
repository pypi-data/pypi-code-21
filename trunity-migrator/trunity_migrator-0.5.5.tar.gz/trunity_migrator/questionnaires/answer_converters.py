"""
Collection of converters that transform T2 answers to list of T3 answer objects.
"""
from typing import List

from trunity_3_client.builders import Answer, TrueFalseAnswer


DEFAULT_SCORE = 1


def convert_multiple_choice(t2_question: dict) -> List[Answer]:
    correct_answer_index = int(t2_question['correct'])
    feedback = t2_question['feedback']

    result = []
    for index, answer in enumerate(t2_question['answers']):
        correct = True if correct_answer_index == index else False
        score = DEFAULT_SCORE if correct else 0

        result.append(
            Answer(answer, correct, score=score, feedback=feedback)
        )

    return result


def convert_multiple_answer(t2_question: dict) -> List[Answer]:
    correct_answer_indexes = [int(index) for index in t2_question['correct']]
    feedback = t2_question['feedback']

    result = []
    for index, answer in enumerate(t2_question['answers']):
        correct = True if index in correct_answer_indexes else False
        score = DEFAULT_SCORE if correct else 0

        result.append(
            Answer(answer, correct, score=score, feedback=feedback)
        )

    return result


def convert_true_false(t2_question: dict) -> List[TrueFalseAnswer]:
    feedback = t2_question['feedback']
    correct = True if t2_question['correct'] == 'true' else False

    def get_score(x: bool):
        return DEFAULT_SCORE if x else 0

    return [
        TrueFalseAnswer(correct, True, score=get_score(correct), feedback=feedback),
        TrueFalseAnswer(not correct, False, score=get_score(not correct), feedback=feedback),
    ]


def convert_short_answer(t2_question: dict) -> List[Answer]:
    feedback = t2_question['feedback']

    return [
        Answer(answer, True, score=DEFAULT_SCORE, feedback=feedback)
        for answer in t2_question['answers']
    ]

