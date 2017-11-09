from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
from django.core.exceptions import ValidationError
from apollo import forms
import copy
import json


#####-----< Layout >----#####
class Layout(models.Model):
    """ a layout controls the positioning and relative sizing of fields in a form."""
    name = models.CharField(max_length=150, unique=True)
    max_width = models.IntegerField(null=True, blank=True, default=None)

    def __str__(self):
        return """%s (%s)""" % (
            self.name, self.id
        )


class LayoutField(models.Model):
    """ the positioning of a field in the forms' layout """
    layout = models.ForeignKey(Layout, related_name='blocks')

    # width and height are in pct relative
    desktop_width = models.DecimalField(max_digits=6, decimal_places=3)
    desktop_height = models.DecimalField(max_digits=6, decimal_places=3)
    desktop_top_left = ArrayField(models.DecimalField(max_digits=6, decimal_places=3), size=2)

    mobile_width = models.DecimalField(max_digits=6, decimal_places=3)
    mobile_height = models.DecimalField(max_digits=6, decimal_places=3)
    mobile_top_left = ArrayField(models.DecimalField(max_digits=6, decimal_places=3), size=2)

    def __str__(self):
        return """%s x %s @ %s (%s)""" % (
            self.desktop_width, self.desktop_height, self.desktop_top_left, self.id
        )


#####-----< Forms >----#####
class Form(models.Model):
    name = models.CharField(max_length=200, unique=True)

    redirect_url = models.CharField(max_length=150, null=True, blank=True, default=None)
    success_message = models.TextField(null=True, blank=True, default=None)
    submit_button_text = models.CharField(max_length=100, default='Submit')
    # if set, submissions go here instead of to our form submission endpoint
    submission_url = models.CharField(max_length=200, null=True, blank=True, default=None)
    # if set, these email addresses will be notified on submissions
    submission_contacts = ArrayField(models.CharField(max_length=400), null=True, blank=True, default=None)

    layout = models.ForeignKey(Layout, related_name='forms', null=True, blank=True, default=None)

    def clone(self):
        """ clone this form to a new form. In addition to the basic fields of this model, this has the effect of copying:
        - associated form fields, creating new copies of fields for the new form

        :return: `Form` a clone of this form
        """
        form_copy = copy.deepcopy(self)

        # make a copy of the base form
        form_copy.pk = None
        form_copy.name = self.name + ' Copy'
        form_copy.save()

        # copy the fields
        for field in self.fields.all():
            field.pk = None
            field.form = form_copy
            field.save()

        return form_copy

    def __str__(self):
        return """%s (%s)""" % (self.name, self.id)


class FormFieldTemplate(models.Model):
    FIELD_TYPES = [
        ('TEXT', 'TEXT'),
        ('HIDDEN', 'HIDDEN'),
        ('TEXTAREA', 'TEXTAREA'),
        ('SELECT', 'SELECT'),
        ('CHECKBOX', 'CHECKBOX'),
        ('RICHTEXT', 'RICHTEXT'),
    ]

    RULE_OPTIONAL = 'OPTIONAL'
    RULE_REQUIRED = 'REQUIRED'
    RULE_EMAIL = 'EMAIL'
    VALIDATION_RULES = [(x, x) for x in [RULE_OPTIONAL, RULE_REQUIRED, RULE_EMAIL]]

    LABEL_TOP = 'TOP'
    LABEL_RIGHT = 'RIGHT'
    LABEL_BOTTOM = 'BOTTOM'
    LABEL_LEFT = 'LEFT'
    LABEL_POSITIONS = [
        (LABEL_TOP, LABEL_TOP),
        (LABEL_RIGHT, LABEL_RIGHT),
        (LABEL_BOTTOM, LABEL_BOTTOM),
        (LABEL_LEFT, LABEL_LEFT),
    ]

    # If True, it means that the value of this field in a submission should be used as the primary label for
    # for the submission
    is_submission_label = models.BooleanField(default=False)

    # Core Fields (Not Overriddeable on FormField instances)
    name = models.CharField(max_length=100, unique=True)
    input_type = models.CharField(max_length=50, choices=FIELD_TYPES, default='text')
    is_visible = models.BooleanField(default=True)

    label = models.CharField(max_length=100, null=True, blank=True, default=None)
    label_position = models.CharField(max_length=50, choices=LABEL_POSITIONS, default=LABEL_TOP)
    placeholder = models.CharField(max_length=150, null=True, blank=True, default=None)
    default_value = models.CharField(max_length=150, null=True, blank=True, default=None)

    value_choices = ArrayField(
        ArrayField(models.CharField(max_length=100), size=2),
        null=True,
        blank=True,
        default=None
    )
    validation_rule = models.CharField(max_length=50, null=True, blank=True, default=RULE_REQUIRED, choices=VALIDATION_RULES)

    def __str__(self):
        return """%s // %s (%s)""" % (self.name, self.input_type, self.id)


class FormField(models.Model):
    """ a form field is a concrete instance of a field on a form. It must be separate from a FormFieldTemplate
    because while the template governs the common configuration of a field, there are certain properties which
    might need overriding on a per-form basis (designated by a leading _)
    """
    form = models.ForeignKey(Form, related_name='fields')
    template = models.ForeignKey(FormFieldTemplate, related_name='instances')
    layout = models.ForeignKey(LayoutField, null=True, blank=True, default=None, on_delete=models.SET_NULL)

    label = models.CharField(max_length=100, null=True, blank=True, default=None)
    label_position = models.CharField(max_length=50, null=True, blank=True, default=FormFieldTemplate.LABEL_TOP, choices=FormFieldTemplate.LABEL_POSITIONS)
    default_value = models.CharField(max_length=150, null=True, blank=True, default=None)
    placeholder = models.CharField(max_length=150, null=True, blank=True, default=None)

    index = models.IntegerField(default=0)

    value_choices = ArrayField(
        ArrayField(models.CharField(max_length=100), size=2),
        null=True,
        blank=True,
        default=None
    )
    validation_rule = models.CharField(max_length=50, null=True, blank=True, default=FormFieldTemplate.RULE_REQUIRED, choices=FormFieldTemplate.VALIDATION_RULES)

    @property
    def name(self):
        return self.template.name

    @property
    def input_type(self):
        return self.template.input_type

    @property
    def is_visible(self):
        return self.template.is_visible

    @property
    def is_submission_label(self):
        return self.template.is_submission_label

    @property
    def is_required(self):
        return self.validation_rule != FormFieldTemplate.RULE_OPTIONAL

    def __str__(self):
        return """%s // Form %s (%s)""" % (
            self.name, self.form, self.id
        )


#####-----< Submissions >----#####
class FormSubmission(models.Model):
    form = models.ForeignKey(Form, related_name='submissions')

    raw_data = JSONField()
    cleaned_data = JSONField(blank=True, null=True, default=None)

    is_valid = models.BooleanField(default=True)

    created_time = models.DateTimeField(auto_now_add=True)

    @property
    def label(self):
        """ the label for this submission is governed by the templates of the fields of the form. The first template
        which has `is_submission_label = True` has its field value looked up in the cleaned data and used as the submissions'
        label
        """
        labelling_field = self.form.fields.filter(template__is_submission_label=True).first()

        if not labelling_field or not self.cleaned_data:
            return None

        return self.cleaned_data[labelling_field.name]

    def clean_data(self):
        """ raw_data => cleaned_data. Cleaning is the process of:
        - removing fields from the raw data any fields which don't exist on the form being submitted
        - converting the raw_data, which will be a list of field dictionaries containing data submitted by the client,
        into a dictionary of field name -> field value
        - validating the data
        :return: `dict` of cleaned, validated data
        :raises: ValidationError if the submission fails to validate
        :raises: ValueError if data isn't available to clean / validate
        """
        # raw_data can be of form {'fields': [<field data>]} or [<field data]
        try:
            fields_list = self.raw_data['fields']
        except TypeError:
            fields_list = self.raw_data

        if not fields_list:
            raise ValueError('no data was found in the raw_data')

        named_data = {}

        # transform the fields list into a dictionary, indexed by field names
        fields_dict = {f['name']: f for f in fields_list}

        stored_defaults = dict(self.form.fields.all().values_list('template__name', 'default_value'))

        for fname in stored_defaults:
            if stored_defaults[fname] or fname in fields_dict:
                try:
                    named_data[fname] = fields_dict[fname]['value']
                except KeyError:
                    named_data[fname] = stored_defaults[fname]

        sform = forms.SubmissionForm(apollo_fields=self.form.fields.all(), data=named_data)

        self.is_valid = sform.is_valid()

        if self.is_valid:
            self.cleaned_data = sform.cleaned_data
        else:
            raise ValidationError(json.dumps(sform.errors.as_json()))

        return self.cleaned_data

    def __str__(self):
        return """Submission for %s @ %s (%s)""" % (
            self.form, self.created_time, self.id
        )

    class Meta:
        ordering = ['-created_time', 'is_valid']