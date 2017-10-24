from typing import List
from abc import ABC, abstractmethod

from requests import Session

from trunity_3_client.clients.endpoints import QuestionsClient


class AbstractAnswer(ABC):

    @abstractmethod
    def to_dict(self) -> dict:
        pass

    def __eq__(self, other):
        return self.to_dict() == other.to_dict()


class Answer(AbstractAnswer):

    def __init__(self, text: str, correct: bool, score: int,
                 feedback: str="", ck_editor: bool=False):
        self.text = text
        self.correct = correct
        self.score = score
        self.feedback = feedback
        self.ck_editor = ck_editor

    def to_dict(self) -> dict:
        return {
            'correct': self.correct,
            'text': self.text,
            'cke': self.ck_editor,
            'score': self.score,
            'feedback': self.feedback,
        }


class TrueFalseAnswer(AbstractAnswer):

    def __init__(self, correct: bool, type: bool, score: int, feedback: str=''):
        self.correct = correct
        self.type = type
        self.score = score
        self.feedback = feedback

    def to_dict(self) -> dict:
        return {
            'correct': self.correct,
            'type': self.type,
            'score': self.score,
            'feedback': self.feedback,
        }


class NumericAnswer(AbstractAnswer):

    def __init__(self, correct: bool, tolerance: int, text: int, score: int,
                 feedback: str=''):
        self.correct = correct
        self.tolerance = tolerance
        self.text = text
        self.score = score
        self.feedback = feedback

    def to_dict(self) -> dict:
        return {
            'correct': self.correct,
            'tolerance': self.tolerance,
            'text': self.text,
            'score': self.score,
            'feedback': self.feedback,
        }


class Questionnaire(object):

    def __init__(self, session: Session):
        self._questions = []
        self._client = QuestionsClient(session)

    def add_multiple_choice(self, text: str, answers: List[Answer],
                            separate: bool = False,
                            numeric_labels: bool = False
                            ) -> None:

        self._questions.append({
            'type': 'multiple_choice',
            'text': text,
            'answers': [answer.to_dict() for answer in answers],
            'separate': separate,
            'numeric_labels': numeric_labels,
        })

    def add_multiple_answer(self, text: str, answers: List[Answer],
                            separate: bool = False,
                            numeric_labels: bool = False) -> None:

        self._questions.append({
            'type': 'multiple_answer',
            'text': text,
            'answers': [answer.to_dict() for answer in answers],
            'separate': separate,
            'numeric_labels': numeric_labels,
        })

    def add_true_false(self, text: str, answers: List[TrueFalseAnswer],
                       separate: bool = False) -> None:

        self._questions.append({
            'type': 'true_false',
            'text': text,
            'answers': [answer.to_dict() for answer in answers],
            'separate': separate,
        })

    def add_short_answer(self, text: str, answers: List[Answer],
                         separate: bool = False,
                         numeric_labels: bool = False) -> None:

        self._questions.append({
            'type': 'short_answer',
            'text': text,
            'answers': [answer.to_dict() for answer in answers],
            'separate': separate,
            'numeric_labels': numeric_labels,
        })

    def add_essay(self, text: str, correct_answer: str, score: int,
                  separate: bool=False,
                  numeric_labels: bool=False,
                  answer_cke: bool=False) -> None:

        self._questions.append({
            'type': 'essay',
            'text': text,
            'correct_answer': correct_answer,
            'score': score,
            'separate': separate,
            'numeric_labels': numeric_labels,
            'answer_cke': answer_cke,
        })

    def add_numeric(self, text: str, answers: List[NumericAnswer],
                    separate: bool=False) -> None:

        self._questions.append({
            'type': 'numeric',
            'text': text,
            'answers': [answer.to_dict() for answer in answers],
            'separate': separate,
        })

    def upload(self, questionnaire_id: str):
        print('Start uploading Questionnaire: ', end='')

        for question in self._questions:
            qst_type = question.pop('type')
            attr_name = 'create_' + qst_type
            getattr(self._client, attr_name)(questionnaire_id, **question)

            print('+ ', end='')

        print('\t\t Done!')
