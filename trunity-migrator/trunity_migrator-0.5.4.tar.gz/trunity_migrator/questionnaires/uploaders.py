from trunity_3_client.builders import Questionnaire
from requests import Session

from trunity_migrator.questionnaires.answer_converters import (
    convert_multiple_choice,
    convert_multiple_answer,
    convert_true_false,
    convert_short_answer,
    DEFAULT_SCORE
)


def upload_question_pool(session: Session, questionnaire_id, t2_questions):
    questionnaire = Questionnaire(session)

    # TODO: refactor this (write adapter etc...)
    for question in t2_questions:

        if question['type'] == 'multipleChoice':

            questionnaire.add_multiple_choice(
                text=question.pop('question'),
                answers=convert_multiple_choice(question),
            )

        elif question['type'] == 'multipleAnswer':

            questionnaire.add_multiple_answer(
                text=question.pop('question'),
                answers=convert_multiple_answer(question),
            )

        elif question['type'] == 'trueFalse':

            questionnaire.add_true_false(
                text=question.pop('question'),
                answers=convert_true_false(question),
            )

        elif question['type'] == 'shortAnswer':

            questionnaire.add_short_answer(
                text=question.pop('question'),
                answers=convert_short_answer(question),
            )

        elif question['type'] == 'essay':

            questionnaire.add_essay(
                text=question.pop('question'),
                correct_answer='',
                score=DEFAULT_SCORE
            )

        else:
            pass

    questionnaire.upload(questionnaire_id)

