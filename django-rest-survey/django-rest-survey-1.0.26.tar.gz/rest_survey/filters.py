from rest_framework_filters import FilterSet
from .models import (
    Survey,
    Section,
    Question,
    SurveyedObject,
    Answer,
    OtherAnswer,
)


class OtherAnswerFilter(FilterSet):

    class Meta:

        model = OtherAnswer
        fields = {
            'id': ['exact'],
            'value': ['icontains', ],
            'question': ['exact'],
            'surveyed': ['exact'],
        }


class SurveyFilter(FilterSet):

    class Meta:

        model = Survey
        fields = {
            'id': ['exact'],
            'name': ['icontains']
        }


class SectionFilter(FilterSet):

    class Meta:
        model = Section
        fields = {
            'id': ['exact'],
            'survey_id': ['exact'],
            'title': ['icontains']
        }


class QuestionFilter(FilterSet):

    class Meta:
        model = Question
        fields = {
            'id': ['exact'],
            'survey_id': ['exact'],
            'section_id': ['exact'],
            'type': ['icontains'],
            'text': ['icontains'],
        }


class AnswerFilter(FilterSet):

    class Meta:
        model = Answer
        fields = {
            'id': ['exact'],
            'surveyed_id': ['exact'],
            'question_id': ['exact'],
        }


class SurveyedObjectFilter(FilterSet):

    class Meta:
        model = SurveyedObject
        fields = {
            'id': ['exact'],
            'survey_id': ['exact'],
            'object_id': ['exact'],
            'content_type': ['exact']
        }
