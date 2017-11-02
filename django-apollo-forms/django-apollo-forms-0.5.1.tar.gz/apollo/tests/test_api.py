from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from apollo.factories import FormFactory, FormFieldFactory, FormFieldTemplateFactory, FormSubmissionFactory
from apollo.settings import apollo_settings
from apollo import signals
import factory
import mock
import json
import pdb
import re


def to_underscore_repr(camelcase):
    parts = re.split('[A-Z]', camelcase)

    if len(parts) == 1:
        return parts[0]

    cap_words = re.findall('[A-Z]', camelcase)
    return parts[0] + '_' + '_'.join([cap_words[i].lower() + parts[i + 1] for i in range(len(cap_words))])


class APITestCase(TestCase):
    path = '/graphql'

    def setUp(self):
        self.client = Client()

        patch_send_email = mock.patch('apollo.lib.emails.send', return_value=True)
        self.mock_send_email = patch_send_email.start()

        self.addCleanup(patch_send_email.stop)

    def post(self, mutation=None, variables=None):
        params = {
            'query': mutation,
            'variables': variables
        }

        return self.client.post(self.path, json.dumps(params), content_type='application/json')


class TestCreateFormSubmission(APITestCase):
    def setUp(self):
        super(TestCreateFormSubmission, self).setUp()

        # set up DB constructs
        self.form = FormFactory(id=1, name='Test Form')
        FormFieldFactory(form=self.form, template=FormFieldTemplateFactory(name='test'))

        self.mutation = """
        mutation CreateFormSubmission($submissionData: FormSubmissionInput, $formId: Int) {
            createFormSubmission(submissionData: $submissionData, formId: $formId) {
                status,
                message
            }
        }
        """

        self.submission_data = {
            'fields': [
                {
                    'id': 1,
                    'name': 'test',
                    'inputType': 'TEXT',
                    'isVisible': True,
                    'label': 'Test',
                    'validationRule': 'OPTIONAL',
                    'value': 'Testy',
                }
            ]
        }

    def _resp_data(self, resp):
        parsed = json.loads(resp.content)
        return parsed['data']['createFormSubmission']

    @factory.django.mute_signals(signals.form_submission_cleaned)
    def test_returns_status_of_success_on_success(self):
        with mock.patch('apollo.models.FormSubmission.clean_data', return_value={}) as mock_clean_data:
            resp = self.post(mutation=self.mutation, variables={
                'submissionData': self.submission_data,
                'formId': 1
            })

            self.assertEqual(mock_clean_data.call_count, 1)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(self._resp_data(resp)['status'], 'success')

    @factory.django.mute_signals(signals.form_submission_cleaned)
    def test_returns_status_of_error_on_value_error(self):
        with mock.patch('apollo.models.FormSubmission.clean_data', side_effect=ValueError) as mock_clean_data:
            resp = self.post(mutation=self.mutation, variables={
                'submissionData': self.submission_data,
                'formId': 1
            })

            self.assertEqual(mock_clean_data.call_count, 1)
            self.assertEqual(self._resp_data(resp)['status'], 'error')
            self.assertEqual(self._resp_data(resp)['message'], 'got error cleaning submission data')

    def test_returns_status_of_error_on_validation_error(self):
        with mock.patch('apollo.models.FormSubmission.clean_data', side_effect=ValidationError('error validating')) as mock_clean_data:
            resp = self.post(mutation=self.mutation, variables={
                'submissionData': self.submission_data,
                'formId': 1
            })

            self.assertEqual(mock_clean_data.call_count, 1)
            self.assertEqual(self._resp_data(resp)['status'], 'error')
            self.assertEqual(self._resp_data(resp)['message'], 'got error validating submission data')

    @factory.django.mute_signals(signals.form_submission_cleaned)
    def test_creates_new_submission_instance_when_clean_succeeds(self):

        resp = self.post(mutation=self.mutation, variables={
            'submissionData': self.submission_data,
            'formId': 1
        })

        self.assertEqual(self._resp_data(resp)['status'], 'success')

        created_submission = self.form.submissions.first()

        self.assertDictEqual(
            created_submission.raw_data,
            {'fields': [{to_underscore_repr(k): v for f in self.submission_data['fields'] for k,v in f.items()}]}
        )
        self.assertDictEqual(created_submission.cleaned_data, {'test': 'Testy'})

    def test_still_creates_submission_when_clean_fails(self):
        with mock.patch('apollo.models.FormSubmission.clean_data', side_effect=ValidationError('error validating')) as mock_clean_data:
            resp = self.post(mutation=self.mutation, variables={
                'submissionData': self.submission_data,
                'formId': 1
            })

            self.assertEqual(self._resp_data(resp)['status'], 'error')
            self.assertEqual(self._resp_data(resp)['message'], 'got error validating submission data')
            self.assertEqual(self.form.submissions.count(), 1)
            self.assertIsNone(self.form.submissions.first().cleaned_data)

    @factory.django.mute_signals(signals.form_submission_cleaned)
    def test_sends_email_to_submission_contacts_when_set(self):
        self.post(mutation=self.mutation, variables={
            'submissionData': self.submission_data,
            'formId': 1
        })

        self.assertEqual(self.mock_send_email.call_count, 0, "shouldnt send email when form has no submission contacts")

        # now try with submission contacts
        self.form.submission_contacts = ['bobby@classaction.com']
        self.form.save()

        self.post(mutation=self.mutation, variables={
            'submissionData': self.submission_data,
            'formId': 1
        })

        self.assertEqual(self.mock_send_email.call_count, 1)
        self.assertIsNone(
            self.mock_send_email.assert_called_with(
                from_email=apollo_settings.SUBMISSION_EMAIL_FROM,
                to_emails=[u'bobby@classaction.com'],
                subject='Apollo: New Form Submission',
                content='new form submission, data = %s' % {u'test': u'Testy'}
            )
        )
