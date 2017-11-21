from trunity_3_client.builders import Questionnaire
from requests import Session

from trunity_migrator.self_assessments.answer_converters import (
    convert_multiple_choice,
    DEFAULT_SCORE,
)


def upload_self_assessment(session: Session, questionnaire_id, t2_questions):
    questionnaire = Questionnaire(session)

    # TODO: refactor this (write adapter etc...)
    for question in t2_questions:

        if question['questionType'] == 'Multiple Choice':

            questionnaire.add_multiple_choice(
                text=question.pop('question'),
                answers=convert_multiple_choice(question),
            )

        elif question['questionType'] == 'Free Response':

            # T2 'Free Response' type in Self-Assessments corresponds
            # to 'Essay' in T3:
            questionnaire.add_essay(
                text=question.pop('question'),
                correct_answer=question['questionFeedback'],
                score=DEFAULT_SCORE
            )

        else:
            pass

    questionnaire.upload(questionnaire_id)
