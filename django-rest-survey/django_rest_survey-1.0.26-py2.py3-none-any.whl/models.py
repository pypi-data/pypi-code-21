# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext as _
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from mptt.models import MPTTModel, TreeForeignKey
from jsonfield import JSONField
from ordered_model.models import OrderedModel
from common.models import (
    DateCreatedMixIn,
    DateUpdatedMixIn,
    CreatedByMixIn
)
from .utils import answer_question
from .choices import (
    QUESTION_TYPE_CHOICES,
    QUESTION_TYPE_TEXT,
)


def default_validators():

    return ['required', ]


@python_2_unicode_compatible
class Survey(DateCreatedMixIn,
             DateUpdatedMixIn,
             CreatedByMixIn):

    '''
    Models out a survey class
    '''

    name = models.CharField(
        max_length=128,
        verbose_name=_('Name')
    )

    active = models.BooleanField(
        verbose_name=_('Active?'),
        default=True
    )

    def answer_question(self, content_type_id, object_id, question_name, value):
        """
        answers a question
        """
        return answer_question(
            survey=self,
            content_type_id=content_type_id,
            object_id=object_id,
            question_name=question_name,
            value=value
        )

    def clone(self, new_name):
        """
        Clones a survey and it's questions
        to a new survey with a new name
        """
        pass

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Survey')
        verbose_name_plural = _('Surveys')


@python_2_unicode_compatible
class Section(DateCreatedMixIn,
              DateUpdatedMixIn,
              CreatedByMixIn,
              OrderedModel,):

    survey = models.ForeignKey(
        Survey,
        related_name='sections'
    )

    title = models.CharField(
        max_length=128,
        verbose_name=_('Title')
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Section')
        verbose_name_plural = _('Sections')
        ordering = ('survey', 'order', )


@python_2_unicode_compatible
class Question(MPTTModel,
               DateCreatedMixIn,
               DateUpdatedMixIn,
               CreatedByMixIn,
               OrderedModel):

    """
    models a survey question
    """

    survey = models.ForeignKey(
        Survey,
        related_name='questions'
    )

    section = models.ForeignKey(
        Section,
        related_name='questions',
    )

    parent = TreeForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='children',
        db_index=True
    )

    parent_value = models.CharField(
        max_length=256,
        verbose_name=_('Parent Value'),
        help_text=_('Value that enables the user to answer the children questions.'),
        null=True
    )

    type = models.CharField(
        max_length=32,
        verbose_name=_('Question Type'),
        choices=QUESTION_TYPE_CHOICES,
        default=QUESTION_TYPE_TEXT
    )

    text = models.CharField(
        max_length=512,
        verbose_name=_('Text')
    )

    help = models.CharField(
        max_length=512,
        verbose_name=_('Help'),
        null=True
    )

    validators = JSONField(
        verbose_name=_('Validators'),
        help_text=_('Validators to be applied at front-end level.'),
        default=default_validators
    )

    other_token = models.CharField(
        verbose_name=_('Other Token'),
        max_length=16,
        null=True
    )

    options = JSONField(
        verbose_name=_('Options'),
        help_text=_('Options to be used, if the field is SELECT, RADIO, CHECKBOX or GRID.'),
        null=True
    )

    order_with_respect_to = ('survey', 'section', 'parent', 'order', )

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')


@python_2_unicode_compatible
class SurveyedObject(DateCreatedMixIn,
                     DateUpdatedMixIn,
                     CreatedByMixIn):

    survey = models.ForeignKey(
        Survey,
        related_name='surveyeds'
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )

    object_id = models.PositiveIntegerField()

    content_object = GenericForeignKey(
        'content_type',
        'object_id'
    )

    def __str__(self):
        return str(self.id)

    class Meta:

        verbose_name = _('Surveyed Object')
        verbose_name_plural = _('Surveyed Objects')


@python_2_unicode_compatible
class Answer(DateCreatedMixIn,
             DateUpdatedMixIn,
             CreatedByMixIn):

    """
    answer model
    """

    surveyed = models.ForeignKey(
        SurveyedObject,
        related_name='answers'
    )

    question = models.ForeignKey(
        Question,
        related_name='answers'
    )

    value = JSONField(
        verbose_name=_('Value'),
        null=True
    )

    def __str__(self):
        return self.value

    class Meta:
        verbose_name = _('Answer')
        verbose_name_plural = _('Answers')
        unique_together = ('surveyed', 'question', )


@python_2_unicode_compatible
class OtherAnswer(DateCreatedMixIn,
                  DateUpdatedMixIn):

    """
    model to store other answers
    for each possible question
    """

    surveyed = models.ForeignKey(
        SurveyedObject,
        related_name='others'
    )

    question = models.ForeignKey(
        Question,
        related_name='others'
    )

    value = models.CharField(
        max_length=256,
        verbose_name=_('Value')
    )

    def __str__(self):
        return self.value

    class Meta:

        unique_together = ('question', 'surveyed', )
