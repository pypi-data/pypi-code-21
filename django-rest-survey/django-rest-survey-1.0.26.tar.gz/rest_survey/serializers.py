# unicode: utf-8
from rest_framework.reverse import reverse
from rest_framework import serializers
from common.serializers import LinkSerializer
from .utils import (
    reverse_list,
    build_fieldsets,
    build_schema,
    build_question_name,
)
from .models import (
    Survey,
    Section,
    Question,
    SurveyedObject,
    Answer,
    OtherAnswer,
)


class QuestionSerializer(LinkSerializer):
    """
    survey serializer
    """

    options = serializers.JSONField()

    def get_links(self, obj):
        request = self.context['request']
        links = {
            'self': reverse('question-detail',
                            kwargs={'pk': obj.pk},
                            request=request),
            'survey': reverse('survey-detail',
                              kwargs={'pk': obj.survey_id}),

        }
        if obj.section:
            links['section'] = reverse('section-detail',
                                       kwargs={'pk': obj.section_id},
                                       request=request)

        if obj.parent:
            links['parent'] = reverse('question-detail',
                                      kwargs={'pk': obj.parent_id},
                                      request=request)
        return links

    class Meta:
        model = Question
        fields = (
            'id',
            'date_created',
            'date_updated',
            'created_by',
            'order',
            'survey',
            'section',
            'parent',
            'parent_value',
            'type',
            'text',
            'help',
            'options',
            'links',
        )


class SectionSerializer(LinkSerializer):
    """
    section serializer
    """
    def get_links(self, obj):
        request = self.context['request']
        links = {
            'self': reverse('section-detail',
                            kwargs={'pk': obj.pk},
                            request=request),
            'survey': reverse('survey-detail',
                              kwargs={'pk': obj.survey_id},
                              request=request),
            'questions': reverse_list(request,
                                      'question-list',
                                      'section_id',
                                      obj.pk)
        }

        return links

    class Meta:
        model = Section
        fields = (
            'id',
            'date_created',
            'date_updated',
            'created_by',
            'order',
            'survey',
            'title',
            'links',
        )


class SurveySerializer(LinkSerializer):
    """
    survey serializer
    """

    survey_data = serializers.SerializerMethodField()

    def get_survey_data(self, obj):
        return {
            'fieldsets': build_fieldsets(obj),
            'schema': build_schema(obj)
        }

    def get_links(self, obj):
        """
        returns all the relevant links
        for the survey model in the serializer
        """

        request = self.context['request']
        return {
            'self': reverse('survey-detail',
                            kwargs={'pk': obj.pk},
                            request=request),
            'sections': reverse_list(request,
                                     'section-list',
                                     'survey_id',
                                     obj.pk),
            'questions': reverse_list(request,
                                      'question-list',
                                      'survey_id',
                                      obj.pk),
            'surveyeds': reverse_list(request,
                                      'surveyedobject-list',
                                      'survey_id',
                                      obj.pk),
        }

    class Meta:
        model = Survey
        fields = (
            'id',
            'date_created',
            'date_updated',
            'created_by',
            'name',
            'active',
            'survey_data',
            'links',
        )


class SurveyedObjectSerializer(LinkSerializer):
    """
    survey serializer
    """

    survey_data = serializers.SerializerMethodField()

    def get_survey_data(self, obj):
        return {build_question_name(a.question): a.value
                for a in obj.answers.all()}

    def get_links(self, obj):
        request = self.context['request']
        links = {
            'self': reverse('surveyedobject-detail',
                            kwargs={'pk': obj.pk},
                            request=request),
            'answers': reverse_list(request,
                                    'question-list',
                                    'surveyedobject_id',
                                    obj.pk),
            'survey': reverse('survey-detail',
                              kwargs={'pk': obj.survey_id},
                              request=request)
        }
        return links

    class Meta:
        model = SurveyedObject
        fields = (
            'id',
            'content_type',
            'object_id',
            'links',
            'survey_data'
        )


class AnswerSerializer(LinkSerializer):
    """
    survey serializer
    """
    def get_links(self, obj):
        request = self.context['request']
        links = {
            'self': reverse('answer-detail',
                            kwargs={'pk': obj.pk},
                            request=request),
            'surveyed': reverse('surveyedobject-detail',
                                kwargs={'pk': obj.surveyed_id},
                                request=request),
            'question': reverse('question-detail',
                                kwargs={'pk': obj.question_id},
                                request=request),
        }
        return links

    class Meta:
        model = Answer
        fields = (
            'id',
            'surveyed',
            'question',
            'value',
            'links',
        )


class OtherAnswerSerializer(LinkSerializer):
    """
    survey serializer
    """
    def get_links(self, obj):
        request = self.context['request']
        return {
            'self': reverse('otheranswer-detail',
                            kwargs={'pk': obj.pk},
                            request=request),
            'surveyed': reverse('surveyedobject-detail',
                                kwargs={'pk': obj.surveyed_id},
                                request=request),
            'question': reverse('question-detail',
                                kwargs={'pk': obj.question_id},
                                request=request)
        }

    class Meta:

        model = OtherAnswer
        fields = (
            'id',
            'question',
            'value',
            'surveyed',
            'links',
        )
