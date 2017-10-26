# coding: utf-8
from rest_framework.reverse import reverse

from .choices import (
    QUESTION_TYPE_RADIO,
    QUESTION_TYPE_SELECT,
    QUESTION_TYPE_CHECKBOXES,
    QUESTION_TYPE_GRID
)


def answer_question(survey,
                    content_type_id,
                    object_id,
                    question_name,
                    value):
    """
    Answer a question for a single survey taken.

    this method should take care of it all.
    """
    from .models import (
        Answer,
        OtherAnswer,
        SurveyedObject,
    )
    try:
        new_survey = False
        surveyed = SurveyedObject.objects.get(
            content_type_id=content_type_id,
            object_id=object_id,
            survey_id=survey.pk
        )
    except SurveyedObject.DoesNotExist:
        new_survey = True
        surveyed = SurveyedObject(
            content_type_id=content_type_id,
            object_id=object_id,
            survey_id=survey.pk
        )

    question = get_question_by_name(question_name)
    if not question:
        raise ValueError('question does not exist')

    if question.survey_id != survey.pk:
        raise ValueError('question does not belong to this questionary')

    # possibilities
    # new survey and new question
    # old survey and new question
    # old survey and old question
    # this determines what is the case and updates/creates the answer value
    if not new_survey:
        # old survey
        try:
            # old question
            answer = Answer.objects.get(
                surveyed_id=surveyed.pk,
                question_id=question.pk
            )
        except Answer.DoesNotExist:
            # new question
            answer = Answer(
                surveyed=surveyed,
                question=question
            )
    else:
        # new survey and new question
        surveyed.save()
        answer = Answer(
            surveyed=surveyed,
            question=question
        )

    if value is None:
        answer.value = value
        answer.save()
        return answer

    answer.value = value

    if question.other_token:
        if question.other_token in value:

            question_options = question.options['values']
            question_options_upper = set([q.upper() for q in question_options])
            question_options_upper.add(question.other_token.upper())
            upper_value = [v.upper() if v else None for v in value]

            if set(upper_value).difference(question_options_upper):
                other_value = set(upper_value).difference(question_options_upper).pop()
                if other_value:
                    create_or_update_other_answer(surveyed, question, other_value)
                upper_value.remove(other_value)
                question_options.append(question.other_token)

            else:
                upper_value.remove(question.other_token.upper())
                delete_other_answer(surveyed, question)

            answer.value = get_options_in_upper(question_options, upper_value)

        else:
            delete_other_answer(surveyed, question)

    answer.save()
    return answer


def create_or_update_other_answer(surveyed, question, value):
    from .models import OtherAnswer
    try:
        other_answer = OtherAnswer.objects.get(question=question, surveyed=surveyed)
        other_answer.value = value
        other_answer.save()
    except OtherAnswer.DoesNotExist:
        OtherAnswer.objects.create(
            surveyed=surveyed,
            question=question,
            value=value.upper()
        )


def delete_other_answer(surveyed, question):
    from .models import OtherAnswer
    try:
        other_answer = OtherAnswer.objects.get(question=question, surveyed=surveyed)
        other_answer.delete()
    except OtherAnswer.DoesNotExist:
        return


def get_options_in_upper(options, upper):
    result = []
    for opt in options:
        if opt.upper() in upper:
            result.append(opt)

    return result


def reverse_list(request, view_name, field, obj):

    """
    reverses a list name
    """
    return reverse(view_name, request=request) + '?{0}={1}'.format(field, obj)


def build_survey_data(survey):
    """
    From a survey, build survey
    data.

    survey_data is a dict with all
    the options, ready for rendering
    """
    return {
        'schema': build_schema(survey),
        'fieldsets': build_fieldsets(survey)
    }


def build_answer(answer):

    return {build_question_name(answer.question): answer.value}


def build_answers(surveyed):

    answer_data = {}
    for a in surveyed.answers:
        answer_data.update(build_answer(a))
    return answer_data


def get_question_by_name(question_name):

    from .models import Question
    if question_name.startswith('q'):
        return Question.objects.get(id=int(question_name[1:]))

    return None


def build_question_name(question):

    return 'q' + str(question.id)


def build_fieldset_name(section):
    return 'f' + str(section.id)


def build_question(question):
    question_data = {}
    question_name = build_question_name(question)
    question_data[question_name] = {
        'name': question_name,
        'title': question.text,
        'help': question.help,
        'type': question.type,
        'options': question.options
    }
    if question.type in (QUESTION_TYPE_RADIO,
                         QUESTION_TYPE_SELECT,
                         QUESTION_TYPE_CHECKBOXES):

        question_data[question_name]['options'] = question.options['values']
        if question.other_token:
            question_data[question_name]['options'].append(question.other_token)
            question_data[question_name]['otherToken'] = question.other_token

    if question.type == QUESTION_TYPE_GRID:
        question_data[question_name]['columns'] = question.options.get('columns')
        question_data[question_name]['rows'] = question.options.get('rows')

    if question.validators:
        question_data[question_name]['validators'] = question.validators

    if question.parent:
        question_data[question_name]['parent'] = build_question_name(question.parent)
        question_data[question_name]['parent_value'] = question.parent_value

    return question_data


def build_schema(survey):
    schema = {}
    questions = survey.questions.all()
    for q in questions:
        schema.update(build_question(q))
    return schema


def build_fieldsets(survey):
    fieldsets = []
    sections = survey.sections.all()
    for section in sections:
        fieldsets.append(
            {
                'legend': section.title,
                'fields': [build_question_name(q) for q in section.questions.all().order_by('id')],
                'name': build_fieldset_name(section)
            }
        )
    return fieldsets
