from typing import List

from trunity_3_client.utils.url import Url, API_ROOT


base_url = Url(API_ROOT)
base_url.tail = 'questions'


class QuestionsClient(object):

    _base_url = base_url.list

    def __init__(self, session):
        self._session = session

    def create_multiple_choice(self, questionnaire_id: str,
                               text: str,
                               answers: List[dict],
                               separate: bool=False,
                               numeric_labels: bool=False
                               ) -> str:
        """
        Example of json:
        {
            "questionnaire_id": "59ad2231aa057f04bce89f20",
            "question": {
              "text": "Test Q json",
              "separate": true,
              "numeric_labels": true,
              "answers": [
                {"correct": false, "text": "answer1 text", "cke": false, "score": 0, "feedback": ""},
                {"correct": false, "text": "answer2 text", "cke": false, "score": 0, "feedback": ""},
                {"correct": true, "text": "<b>answer3 text</b>", "cke": true, "score": 1, "feedback": "Some"}
              ]
            }
        }
        """
        data = {
            'questionnaire_id': questionnaire_id,
            'question': {
                'text': text,
                'separate': separate,
                'numeric_labels': numeric_labels,
                'answers': answers,
            },
        }

        url = self._base_url + '/multiple_choice'

        response = self._session.post(url, json=data)

        response.raise_for_status()
        return response.json()['question_id']

    def create_multiple_answer(self, questionnaire_id: str,
                               text: str,
                               answers: List[dict],
                               separate: bool = False,
                               numeric_labels: bool = False
                               ) -> str:
        """
          {
            "questionnaire_id": "59ad2231aa057f04bce89f20",
            "question": {
              "text": "Test Q json",
              "separate": true,
              "numeric_labels": true,
              "answers": [
                {"correct": false, "text": "answer1 text", "score": 0, "feedback": ""},
                {"correct": true, "text": "answer2 text", "cke": false, "score": 1, "feedback": "Some"},
                {"correct": true, "text": "<b>answer3 text</b>", "cke": true, "score": 1, "feedback": ""}
              ]
            }
        }

        :return: question_id
        """
        data = {
            'questionnaire_id': questionnaire_id,
            'question': {
                'text': text,
                'separate': separate,
                'numeric_labels': numeric_labels,
                'answers': answers,
            },
        }

        url = self._base_url + '/multiple_answer'

        response = self._session.post(url, json=data)

        response.raise_for_status()
        return response.json()['question_id']

    def create_true_false(self, questionnaire_id: str,
                          text: str,
                          answers: List[dict],
                          separate: bool = False,
                          ) -> str:
        """
        Example of json:
        {
            "questionnaire_id": "59ad2231aa057f04bce89f20",
            "question": {
              "text": "Test Q json",
              "separate": true,

              "answers": [
                {"correct": false, "type": true, "score": 0, "feedback": ""},
                {"correct": true, "type": false, "score": 1, "feedback": "Some"}
              ]
            }
        }
        """
        data = {
            'questionnaire_id': questionnaire_id,
            'question': {
                'text': text,
                'separate': separate,
                'answers': answers,
            },
        }

        url = self._base_url + '/true_false'

        response = self._session.post(url, json=data)

        response.raise_for_status()
        return response.json()['question_id']

    def create_short_answer(self, questionnaire_id: str,
                            text: str,
                            answers: List[dict],
                            separate: bool = False,
                            numeric_labels: bool = False
                            ):
        """
        JSON example:
         {
            "questionnaire_id": "59ad2231aa057f04bce89f20",
            "question": {
              "text": "Test Q json",
              "separate": true,
              "numeric_labels": true,
              "answers": [
                {"correct": false, "text": "answer1 text", "cke": false, "score": 0, "feedback": ""},
                {"correct": true, "text": "<b>answer2 text</b>", "cke": true, "score": 1, "feedback": "Some"}
              ]
            }
        }


        :return: question_id
        """
        data = {
            'questionnaire_id': questionnaire_id,
            'question': {
                'text': text,
                'separate': separate,
                'numeric_labels': numeric_labels,
                'answers': answers,
            },
        }

        url = self._base_url + '/short_answer'

        response = self._session.post(url, json=data)

        response.raise_for_status()
        return response.json()['question_id']

    def create_essay(self, questionnaire_id: str,
                     text: str,
                     correct_answer: str,
                     score: int,
                     separate: bool=False,
                     numeric_labels: bool=False,
                     answer_cke: bool=False
                     ):
        """
        Example of json:
          {
                "questionnaire_id": "59ad2231aa057f04bce89f20",
                "question": {
                  "text": "Test Q json",
                  "separate": true,
                  "correct_answer": "<b>Text</b>",
                  "answer_cke": false,
                  "score": 1
                }
            }
        """
        data = {
            'questionnaire_id': questionnaire_id,
            'question': {
                'text': text,
                'separate': separate,
                'correct_answer': correct_answer,
                'numeric_labels': numeric_labels,
                'answer_cke': answer_cke,
                'score': score,
            },
        }

        url = self._base_url + '/essay'

        response = self._session.post(url, json=data)

        response.raise_for_status()
        return response.json()['question_id']

    def create_numeric(self, questionnaire_id: str,
                       text: str,
                       answers: List[dict],
                       separate: bool=False
                       ) -> str:
        """
        Example of json:
          {
                "questionnaire_id": "59ad2231aa057f04bce89f20",
                "question": {
                  "text": "Test Q json",
                  "separate": true,
                  "answers": [
                    {"correct": false, "tolerance": 1, "text": 23, "score": 0, "feedback": ""},
                    {"correct": true, "tolerance": 2, "text": 32, "score": 1, "feedback": "Some"}
                  ]
                }
            }
        """
        data = {
            'questionnaire_id': questionnaire_id,
            'question': {
                'text': text,
                'separate': separate,
                'answers': answers,
            },
        }

        url = self._base_url + '/numeric'

        response = self._session.post(url, json=data)

        response.raise_for_status()
        return response.json()['question_id']

