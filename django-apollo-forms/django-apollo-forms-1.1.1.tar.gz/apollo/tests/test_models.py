from django.test import TestCase
from django.core.exceptions import ValidationError
from apollo.models import FormFieldTemplate
from apollo.factories import FormFactory, FormFieldFactory, FormFieldTemplateFactory, FormSubmissionFactory
import mock


#####-----< Form Submissions >----#####
class FormSubmissionTestCase(TestCase):
    default_raw_data = [
        {'name': 'name', 'value': 'bob', 'id': 1, 'validation_rule': 'REQUIRED'},
        {'name': 'email', 'value': 'bob@test.com', 'id': 2, 'validation_rule': 'EMAIL'}
    ]

    def setUp(self):
        self.form = FormFactory.create()


class TestFormSubmissionLabel(FormSubmissionTestCase):
    def test_label_is_email(self):
        FormFieldFactory(
            form=self.form,
            template=FormFieldTemplateFactory(name='name', is_submission_label=False)
        )
        FormFieldFactory(
            form=self.form,
            template=FormFieldTemplateFactory(name='email', is_submission_label=True)
        )

        submission = FormSubmissionFactory(form=self.form, raw_data=self.default_raw_data)

        submission.clean_data()

        self.assertEqual(submission.cleaned_data['email'], submission.label)

    def test_no_labelling_field_set(self):
        FormFieldFactory(
            form=self.form,
            template=FormFieldTemplateFactory(name='name', is_submission_label=False)
        )
        FormFieldFactory(
            form=self.form,
            template=FormFieldTemplateFactory(name='email', is_submission_label=False)
        )

        submission = FormSubmissionFactory(form=self.form, raw_data=self.default_raw_data)

        submission.clean_data()

        self.assertIsNone(submission.label)


class TestFormSubmissionCleanData(FormSubmissionTestCase):
    def setUp(self):
        super(TestFormSubmissionCleanData, self).setUp()

        self.field_name = FormFieldFactory(
            form=self.form,
            default_value='Bob',
            template=FormFieldTemplateFactory(name='name')
        )
        self.field_email = FormFieldFactory(
            form=self.form,
            template=FormFieldTemplateFactory(name='email')
        )

    def test_applies_cleaning_to_raw_data(self):
        submission = FormSubmissionFactory(form=self.form, raw_data={'fields': self.default_raw_data})

        submission.clean_data()

        self.assertDictEqual(
            submission.cleaned_data,
            {
                'email': 'bob@test.com',
                'name': 'bob'
            }
        )

    def test_applying_cleaning_to_raw_data_as_list_is_equivalent(self):
        self.assertDictEqual(
            FormSubmissionFactory(form=self.form, raw_data=self.default_raw_data).clean_data(),
            FormSubmissionFactory(form=self.form, raw_data={'fields': self.default_raw_data}).clean_data()
        )

    def test_strips_fields_not_in_form(self):
        raw_data = {
            'fields': [
                {'name': 'name', 'value': 'bob', 'id': 1, 'validation_rule': 'REQUIRED'},
                {'name': 'email', 'value': 'bob@test.com', 'id': 2, 'validation_rule': 'EMAIL'},
                {'name': 'phone_number', 'value': '1234567890', 'id': 3, 'validation_rule': 'REQUIRED'}
            ]
        }

        submission = FormSubmissionFactory(form=self.form, raw_data=raw_data)

        submission.clean_data()

        self.assertDictEqual(
            submission.cleaned_data,
            {
                'email': 'bob@test.com',
                'name': 'bob'
            }
        )

    def test_adds_fields_not_submitted_and_with_default_values_to_form(self):
        raw_data = [
            {'name': 'email', 'value': 'bob@test.com', 'id': 2, 'validation_rule': 'EMAIL'}
        ]

        submission = FormSubmissionFactory(form=self.form, raw_data=raw_data)

        submission.clean_data()

        self.assertDictEqual(
            submission.cleaned_data,
            {
                'email': 'bob@test.com',
                'name': self.field_name.default_value
            }
        )

    def test_uses_default_field_value_when_field_has_no_value(self):
        raw_data = {
            'fields': [
                {'name': 'name', 'id': 1, 'validation_rule': 'REQUIRED'},
                {'name': 'email', 'value': 'bob@test.com', 'id': 2, 'validation_rule': 'EMAIL'},
            ]
        }

        submission = FormSubmissionFactory(form=self.form, raw_data=raw_data)

        submission.clean_data()

        self.assertDictEqual(
            submission.cleaned_data,
            {
                'email': 'bob@test.com',
                'name': self.field_name.default_value
            }
        )

    @mock.patch('apollo.forms.SubmissionForm.is_valid', return_value=False)
    def test_raises_validation_error_if_validation_fails(self, mock_is_valid):
        raw_data = [
            {'name': 'email', 'value': 'bob@test.com', 'id': 2, 'validation_rule': 'EMAIL'}
        ]

        submission = FormSubmissionFactory(form=self.form, raw_data=raw_data)

        self.assertRaises(ValidationError, submission.clean_data)
        self.assertFalse(submission.is_valid)

    def test_sets_is_valid_field_on_submission(self):
        raw_data = [
            {'name': 'email', 'value': 'bob@test.com', 'id': 2, 'validation_rule': 'EMAIL'}
        ]

        submission = FormSubmissionFactory(form=self.form, raw_data=raw_data)

        submission.clean_data()

        self.assertTrue(submission.is_valid)