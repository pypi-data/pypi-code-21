import re
import random
import requests
import furl
import base64
import json
from datetime import datetime
import uuid

from fhirclient.models.patient import Patient
from fhirclient.models.list import List, ListEntry
from fhirclient.models.organization import Organization
from fhirclient.models.codeableconcept import CodeableConcept
from fhirclient.models.coding import Coding
from fhirclient.models.flag import Flag
from fhirclient.models.fhirreference import FHIRReference
from fhirclient.models.bundle import Bundle, BundleEntry, BundleEntryRequest
from fhirclient.models.period import Period
from fhirclient.models.fhirdate import FHIRDate
from fhirclient.models.bundle import Bundle
from fhirclient.models.relatedperson import RelatedPerson
from fhirclient.models.questionnaire import Questionnaire
from fhirclient.models.questionnaireresponse import QuestionnaireResponse

from ppm_fhir import fhir_resources

import logging

logger = logging.getLogger(__name__)


class Participant:

    # Snomed related information.
    SNOMED_LOCATION_CODE = "SNOMED:43741000"
    SNOMED_VERSION_URI = "http://snomed.info/sct/900000000000207008"

    # Define related resources to be managed for each Patient
    ENROLLMENT = 'enrollment'
    CONSENT = 'consent'
    POINTS_OF_CARE = 'points_of_care'
    QUESTIONNAIRE = 'questionnaire'
    RESOURCES = (
        (ENROLLMENT, 'Enrollment'),
        (CONSENT, 'Consent'),
        (POINTS_OF_CARE, 'Points Of Care'),
        (QUESTIONNAIRE, 'Questionnaire'),
    )

    QUESTIONNAIRE_IDS = (
        ('autism', 'asd'),
        ('neer', 'registration-information-for-ppm2'),
    )

    def __init__(self, fhir_url, project, email=None, fhir_id=None, includes=[]):
        self.fhir_url = fhir_url
        self.project = project
        self.email = email
        self.fhir_id = fhir_id
        self.includes = includes

        # Start out with empty data.
        self.data = {}

        # Initialize.
        self.properties = {
            'project': self.project
        }

        # Make the query if possible.
        if self.email or self.fhir_id:
            self._fetch()

        # Update the properties.
        self.properties.update(self._flatten())

    def _fetch(self):

        # Prepare the URL.
        url = furl.furl(self.fhir_url)
        url.path.add('Patient')

        # Check for the fhir ID
        if self.fhir_id:
            url.query.add('_id={}'.format(self.fhir_id))

        elif self.email:
            url.query.add('identifier=http://schema.org/email|{}'.format(self.email))

        else:
            raise RuntimeError('fhir_id or email is required to get Patient')

        # Add additional resources.
        if self.ENROLLMENT in self.includes:
            url.query.add('_revinclude=Flag:subject')

        if self.CONSENT in self.includes:
            url.query.add('_revinclude=Composition:subject&_include=*&_revinclude=RelatedPerson:patient')

        if self.POINTS_OF_CARE in self.includes:
            url.query.add('_revinclude=List:subject&_include=*')

        if self.QUESTIONNAIRE in self.includes:
            url.query.add('_revinclude=QuestionnaireResponse:source&_include=*')

        # Query
        response = requests.get(url.url)
        response.raise_for_status()

        # Retain the response.
        self.data = response.json()

        # Parse the response.
        bundle = response.json()
        if bundle.get('total', 0) == 0:
            raise RuntimeError('Patient could not be found')

        # Update the properties.
        self.properties.update(self._flatten())

    def _flatten(self):

        # Flatten the patient.
        data = self._flatten_patient()

        # Process the related resources.
        if self.ENROLLMENT in self.includes:
            data[self.ENROLLMENT] = self._flatten_enrollment()

        if self.CONSENT in self.includes:
            data[self.CONSENT] = self._flatten_consent()

        if self.POINTS_OF_CARE in self.includes:
            data[self.POINTS_OF_CARE] = self._flatten_points_of_care()

        if self.QUESTIONNAIRE in self.includes:
            data[self.QUESTIONNAIRE] = self._flatten_questionnaire(self.get_questionnaire_id())

        return data

    def get_questionnaire_id(self):
        return dict(self.QUESTIONNAIRE_IDS).get(self.project)

    def has(self, resource):

        # Check valid resource.
        if resource not in dict(self.RESOURCES).keys():
            raise RuntimeError('"{}" is not a supported resource'.format(resource))

        # Call self.
        return getattr(self, '_has_{}'.format(resource))() is not None

    def get(self, resource):

        # Check valid resource.
        if resource not in dict(self.RESOURCES).keys():
            raise RuntimeError('"{}" is not a supported resource'.format(resource))

        # Call self.
        return getattr(self, '_flatten_{}'.format(resource))()

    def add(self, resource):

        # Check valid resource.
        if resource not in dict(self.RESOURCES).keys():
            raise RuntimeError('"{}" is not a supported resource'.format(resource))

        # Call self.
        return getattr(self, '_fetch_{}'.format(resource))()

    def get_resource_url(self, resource_type, fhir_id):

        # Build the URL.
        url = furl.furl(self.fhir_url)

        # Add the resource.
        url.path.segments.append(resource_type)

        # Add the id.
        url.path.segments.append(fhir_id)

        return url.url

    def _has_enrollment(self):

        # Check for the resource.
        conditions = {
            'https://peoplepoweredmedicine.org/enrollment-status': ['code', 'coding', 0, 'system']
        }

        resource = self._get_resource(self.data, 'Flag', conditions=conditions)

        return resource is not None

    def _has_consent(self):

        # Check for the resource.
        conditions = {
            'HRESCH': ['purpose', 0, 'code']
        }

        resource = self._get_resource(self.data, 'Consent', conditions=conditions)

        return resource is not None

    def _has_points_of_care(self):

        # Check for the resource.
        conditions = {
            'SNOMED:43741000': ['code', 'coding', 0, 'code']
        }

        resource = self._get_resource(self.data, 'List', conditions=conditions)

        return resource is not None

    def _has_questionnaire(self):

        # Determine the ID.
        questionnaire_id = self.get_questionnaire_id()

        # Check for the resource.
        conditions = {
            'Questionnaire/{}'.format(questionnaire_id): ['questionnaire', 'reference']
        }

        resource = self._get_resource(self.data, 'QuestionnaireResponse', conditions=conditions)

        return resource is not None

    def _get_resource(self, bundle, resource_type, index=0, conditions=None):

        # Find resources.
        resources = [entry['resource'] for entry in bundle.get('entry', [])
                     if entry['resource']['resourceType'] == resource_type]

        # Check conditions.
        matched = []
        if conditions:

            # Iterate through them and match.
            for condition, path in conditions.items():
                for resource in resources:

                    # Get the value.
                    value = self._get_or(resource, path, None)
                    if value and value == condition:
                        matched.append(resource)
        else:
            matched = resources

        # Return if available
        if index < len(matched):
            return matched[index]

        return None

    def _get_resources(self, bundle, resource_type, conditions=None):

        # Find resources.
        resources = [entry['resource'] for entry in bundle.get('entry', [])
                     if entry['resource']['resourceType'] == resource_type]

        # Check conditions.
        matched = []
        if conditions:

            # Iterate through them and match.
            for condition, path in conditions.items():
                for resource in resources:

                    # Get the value.
                    value = self._get_or(resource, path, None)
                    if value and value == condition:
                        matched.append(resource)

        else:
            matched = resources

        return matched

    def _get_or(self, item, keys, default=''):

        try:
            # Try it out.
            for key in keys:
                item = item[key]

            return item
        except (KeyError, IndexError):
            return default

    def _get_fhir_id(self, resource_id):

        # Get the integer portion.
        match = re.search('(\w+\/)?([a-zA-Z0-9\-_]+)', resource_id)
        if match:
            return match.group(2)

        return None

    def _fetch_patient(self):

        # Prepare the URL.
        url = furl.furl(self.fhir_url)
        url.path.add('Patient')

        # Check for the fhir ID
        if self.fhir_id:
            url.query.add('_id={}'.format(self.fhir_id))

        elif self.email:
            url.query.add('identifier=http://schema.org/email|{}'.format(self.email))

        else:
            raise RuntimeError('fhir_id or email is required to get Patient')

        # Query
        response = requests.get(url.url)
        response.raise_for_status()

        # Retain the response.
        self.data = response.json()

    def _flatten_patient(self):

        # Get the patient resource.
        resource = self._get_resource(self.data, 'Patient')
        data = dict()
        if resource:

            # Get required attributes.
            data["email"] = resource['identifier'][0]['value']
            data["fhir_id"] = resource['id']

            # Get optional items.
            data['firstname'] = self._get_or(resource, ['name', 0, 'given', 0])
            data['lastname'] = self._get_or(resource, ['name', 0, 'family'])

            data['street_address1'] = self._get_or(resource, ['address', 0, 'line', 0])
            data['street_address2'] = self._get_or(resource, ['address', 0, 'line', 1])
            data['city'] = self._get_or(resource, ['address', 0, 'city'])
            data['state'] = self._get_or(resource, ['address', 0, 'state'])
            data['zip'] = self._get_or(resource, ['address', 0, 'postalCode'])

            # Get phone.
            if resource.get('telecom'):
                for telecom in resource['telecom']:
                    if telecom['system'] == "phone":
                        data['phone'] = self._get_or(telecom, ['value'])

            # Get Twitter.
            if resource.get('telecom'):
                for telecom in resource['telecom']:
                    if telecom['system'] == "other":
                        data['twitter'] = self._get_or(telecom, ['value'])

        return data

    def _flatten_points_of_care(self):

        # Get the organizations.
        resources = self._get_resources(self.data, 'Organization')
        data = []

        if resources:
            for resource in resources:
                data.append(get_or(resource, ['name']))

        return data

    def _flatten_enrollment(self):

        # Get the resource.
        resource = self._get_resource(self.data, 'Flag')
        data = dict()
        if resource:
            # Try and get the values
            data['enrollment'] = get_or(resource, ['code', 'coding', 0, 'code'])
            data['status'] = get_or(resource, ['status'])
            data['start'] = get_or(resource, ['period', 'start'])
            data['end'] = get_or(resource, ['period', 'end'])

        return data

    def _flatten_questionnaire(self, questionnaire_id):

        # Get the resources.
        q_resource = self._get_resource(self.data, 'Questionnaire',
                                        conditions={questionnaire_id: ['id']})
        a_resource = self._get_resource(self.data, 'QuestionnaireResponse',
                                        conditions={'Questionnaire/{}'.format(questionnaire_id):
                                                        ['questionnaire', 'reference']})

        # Get each question.
        data = {}
        if q_resource and a_resource:
            for question_index, question in enumerate([item for item in q_resource.get('item', [])
                                                       if item.get('linkId') is not None], 1):

                # Append the index to the question.
                question_text = '{}. {}'.format(question_index, question['text'])

                # Initialize the question's key-value pair.
                data[question_text] = []

                # Get all answers.
                answers = [response for response in a_resource['item']
                           if question['linkId'] == response['linkId']]

                # Find all answers.
                for answer_index, answer in enumerate(answers, 1):

                    # Get the question type.
                    if question.get('type') == 'boolean':

                        # Get the text of the answer.
                        answer_value = 'True' if answer['answer'][0]['valueString'] == '1' else 'False'

                    else:

                        # Get the text of the answer.
                        answer_value = answer['answer'][0]['valueString']

                    # Check for a sub-answer.
                    sub_answer = next((item['answer'][0]['valueString'] for item in a_resource.get('item', [])
                                       if item['linkId'] == '{}-{}'.format(question['linkId'], answer_index)), None)
                    if sub_answer is not None:
                        # Add it.
                        answer_value += ' ({})'.format(sub_answer)

                    # Add it.
                    data[question_text].append(answer_value)

        return data

    def _flatten_consent(self):

        # Prepare the object.
        data = {
            'consent_questionnaires': [],
            'assent_questionnaires': [],
        }
        consent_exceptions = []
        assent_exceptions = []

        # Inject link IDs
        json = inject_link_ids(self.data)

        # Create the bundle object.
        bundle = Bundle(json)
        if bundle.total > 0:

            for bundle_entry in bundle.entry:
                if bundle_entry.resource.resource_type == "Consent":

                    signed_consent = bundle_entry.resource

                    # We can pull the date from the Consent Resource. It's stamped in a few places.
                    data["date_signed"] = signed_consent.dateTime.origval

                    # Exceptions are for when they refuse part of the consent.
                    if signed_consent.except_fhir:
                        for consent_exception in signed_consent.except_fhir:
                            consent_exceptions.append(consent_exception.code[0].display)

                elif bundle_entry.resource.resource_type == 'Composition':

                    composition = bundle_entry.resource

                    entries = [section.entry for section in composition.section if section.entry is not None]
                    references = [entry[0].reference for entry in entries if
                                  len(entry) > 0 and entry[0].reference is not None]
                    text = [section.text.div for section in composition.section if section.text is not None][0]

                    # Check the references for a Consent object, making this comp the consent one.
                    if len([r for r in references if 'Consent' in r]) > 0:
                        data['consent_text'] = text
                    else:
                        data['assent_text'] = text

                elif bundle_entry.resource.resource_type == "RelatedPerson":
                    pass
                elif bundle_entry.resource.resource_type == "Contract":

                    contract = bundle_entry.resource

                    # Contracts with a binding reference are either the individual consent or the guardian consent.
                    if contract.bindingReference:

                        # Get the questionnaire and responses
                        questionnaire_response_id = self._get_fhir_id(contract.bindingReference.reference)
                        questionnaire_response_json = self._get_resource(bundle_, 'QuestionnaireResponse',
                                                                         conditions={questionnaire_response_id: ['id']})
                        # Get the resources.
                        questionnaire_id = self._get_fhir_id(questionnaire_response_json['questionnaire']['reference'])
                        questionnaire_json = self._get_resource(bundle_, 'Questionnaire',
                                                                conditions={questionnaire_id: ['id']})

                        questionnaire = Questionnaire(questionnaire_json)
                        questionnaire_response = QuestionnaireResponse(questionnaire_response_json)

                        # The reference refers to a Questionnaire which is linked to a part of the consent form.
                        if questionnaire_response.questionnaire.reference == "Questionnaire/individual-signature-part-1" \
                                or questionnaire_response.questionnaire.reference == "Questionnaire/neer-signature":

                            # This is a person consenting for themselves.
                            data["type"] = "INDIVIDUAL"
                            data["signor_signature"] = base64.b64decode(contract.signer[0].signature[0].blob)
                            data["participant_name"] = contract.signer[0].signature[0].whoReference.display

                            # These don't apply on an Individual consent.
                            data["participant_acknowledgement_reason"] = "N/A"
                            data["participant_acknowledgement"] = "N/A"
                            data["signor_name"] = "N/A"
                            data["signor_relationship"] = "N/A"
                            data["assent_signature"] = "N/A"
                            data["assent_date"] = "N/A"
                            data["explained_signature"] = "N/A"

                        elif questionnaire_response.questionnaire.reference == "Questionnaire/guardian-signature-part-1":

                            # This is a person consenting for someone else.
                            data["type"] = "GUARDIAN"

                            # Get the Related Person resource who signed the contract.
                            related_person_id = self._get_fhir_id(contract.signer[0].party.reference)
                            related_person_json = self._get_resource(json, 'RelatedPerson',
                                                                     conditions={related_person_id: ['id']})
                            related_person = RelatedPerson(related_person_json)

                            data["signor_name"] = related_person.name[0].text
                            data["signor_relationship"] = related_person.relationship.text

                            data["participant_name"] = contract.signer[0].signature[
                                0].onBehalfOfReference.display
                            data["signor_signature"] = base64.b64decode(contract.signer[0].signature[0].blob)

                        elif questionnaire_response.questionnaire.reference == "Questionnaire/guardian-signature-part-2":

                            # This is the question about being able to get acknowledgement from the participant by the guardian/parent.
                            data["participant_acknowledgement"] = questionnaire_response.item[0].answer[
                                0].valueString

                            # If the answer to the question is no, grab the reason.
                            if data["participant_acknowledgement"] == "no":
                                data["participant_acknowledgement_reason"] = \
                                    questionnaire_response.item[1].answer[0].valueString

                            # This is the Guardian's signature letting us know they tried to explain this study.
                            data["explained_signature"] = base64.b64decode(
                                contract.signer[0].signature[0].blob)

                        elif questionnaire_response.questionnaire.reference == "Questionnaire/guardian-signature-part-3":

                            # A contract without a reference is the assent page.
                            data["assent_signature"] = base64.b64decode(contract.signer[0].signature[0].blob)
                            data["assent_date"] = contract.issued.origval

                            # Append the Questionnaire Text if the response is true.
                            for current_response in questionnaire_response.item:

                                if current_response.answer[0].valueBoolean:
                                    answer = \
                                        [item for item in questionnaire.item if item.linkId == current_response.linkId][
                                            0]
                                    assent_exceptions.append(answer.text)

                        # Prepare to parse the questionnaire.
                        questionnaire_object = {
                            'template': 'dashboard/{}.html'.format(questionnaire.id),
                            'questions': []
                        }

                        for item in questionnaire.item:

                            question_object = {
                                'type': item.type,
                            }

                            if item.type == 'display':
                                question_object['text'] = item.text

                            elif item.type == 'boolean' or item.type == 'question':
                                # Get the answer.
                                for response in questionnaire_response.item:
                                    if response.linkId == item.linkId:
                                        # Process the question, answer and response.
                                        if item.type == 'boolean':
                                            question_object['text'] = item.text
                                            question_object['answer'] = response.answer[0].valueBoolean

                                        elif item.type == 'question':
                                            question_object['yes'] = item.text
                                            question_object[
                                                'no'] = 'I was not able to explain this study to my child or ' \
                                                        'individual in my care who will be participating'
                                            question_object['answer'] = response.answer[0].valueString is 'yes'

                            # Add it.
                            questionnaire_object['questions'].append(question_object)

                            # Check the type.
                    if questionnaire_response.questionnaire.reference == "Questionnaire/guardian-signature-part-3":
                        data['assent_questionnaires'].append(questionnaire_object)
                    else:
                        data['consent_questionnaires'].append(questionnaire_object)

        data["exceptions"] = consent_exceptions
        data["assent_exceptions"] = assent_exceptions

        return data

    def _create_patient(self, form):

        # Build a FHIR-structured Patient resource.
        patient_data = {
            'resourceType': 'Patient',
            'identifier': [
                {
                    'system': 'http://schema.org/email',
                    'value': form.get('email'),
                },
            ],
            'name': [
                {
                    'use': 'official',
                    'family': form.get('lastname'),
                    'given': [form.get('firstname')],
                },
            ],
            'address': [
                {
                    'line': [
                        form.get('street_address1'),
                        form.get('street_address2'),
                    ],
                    'city': form.get('city'),
                    'postalCode': form.get('zip'),
                    'state': form.get('state'),
                }
            ],
            'telecom': [
                {
                    'system': 'phone',
                    'value': form.get('phone'),
                },
            ],
        }

        # Convert the twitter handle to a URL
        if form.get('twitter_handle'):
            patient_data['telecom'].append({
                'system': 'other',
                'value': 'https://twitter.com/' + form['twitter_handle'],
            })

        try:

            # Create a placeholder ID for the patient the flag can reference.
            patient_id = uuid.uuid1().urn

            # Use the FHIR client lib to validate our resource.
            # "If-None-Exist" can be used for conditional create operations in FHIR.
            # If there is already a Patient resource identified by the provided email
            # address, no duplicate records will be created.
            Patient(patient_data)

            patient_request = BundleEntryRequest({
                'url': 'Patient',
                'method': 'POST',
                'ifNoneExist': str(furl.Query({
                    'identifier': 'http://schema.org/email|' + form.get('email'),
                }))
            })
            patient_entry = BundleEntry({
                'resource': patient_data,
                'fullUrl': patient_id
            })
            patient_entry.request = patient_request

            # Validate.
            flag = Flag(fhir_resources.enrollment_flag(patient_id, 'registered'))
            flag_request = BundleEntryRequest({'url': 'Flag', 'method': 'POST'})
            flag_entry = BundleEntry({'resource': flag.as_json()})
            flag_entry.request = flag_request

            # Validate it.
            bundle = Bundle()
            bundle.entry = [patient_entry, flag_entry]
            bundle.type = 'transaction'

            logger.debug("[P2M2][DEBUG][create_user_in_fhir_server]")

            # Create the Patient and Flag on the FHIR server.
            # If we needed the Patient resource id, we could follow the redirect
            # returned from a successful POST operation, and get the id out of the
            # new resource. We don't though, so we can save an HTTP request.
            response = requests.post(self.fhir_url, json=bundle.as_json())

            # Refetch.
            self._fetch()

            return response

        except Exception as e:
            raise

    def _update_enrollment(self, status):

        # Fetch the flag.
        resource = self._get_resource(self.data, 'Flag')

        # Check for nothing.
        if not resource:

            # Create it.
            return self._create_enrollment(status)

        else:
            # Get the first and only flag.
            flag = Flag(resource)
            code = flag.code.coding[0]

            # Update flag properties for particular states.
            if code.code != 'accepted' and status == 'accepted':

                # Set status.
                flag.status = 'active'

                # Set a start date.
                now = FHIRDate(datetime.now().isoformat())
                period = Period()
                period.start = now
                flag.period = period

            elif code.code != 'terminated' and status == 'terminated':

                # Set status.
                flag.status = 'inactive'

                # Set an end date.
                now = FHIRDate(datetime.now().isoformat())
                flag.period.end = now

            else:

                # Flag defaults to inactive with no start or end dates.
                flag.status = 'inactive'
                flag.period = None

            # Set the code.
            code.code = status
            code.display = status.title()
            flag.code.text = status.title()

            # Post it.
            response = requests.put(self.get_resource_url('Flag', flag.id), json=flag.as_json())

            # Refetch
            self._fetch()

            return response

    def _create_enrollment(self, status='registered'):

        # Use the FHIR client lib to validate our resource.
        flag = Flag(fhir_resources.enrollment_flag(self.fhir_id, status))

        # Set a date if enrolled.
        if status == 'accepted':
            now = FHIRDate(datetime.now().isoformat())
            period = Period()
            period.start = now
            flag.period = period

        # Build the FHIR Flag destination URL.
        url = furl.furl(self.FHIR_URL)
        url.path.segments.append('Flag')

        response = requests.post(url.url, json=flag.as_json())

        # Refetch
        self._fetch()

        return response

    ############################  ##############  ##############  ##############  ##############  ##############  ##############
    ##############  ##############  ##############  ##############  ##############  ##############  ##############
    ##############  ##############  ##############  ##############  ##############  ##############
    ############################  ##############  ##############  ##############  ##############  ##############  ##############
    ##############  ##############  ##############  ##############  ##############  ##############  ##############
    ##############  ##############  ##############  ##############  ##############  ##############
    ############################  ##############  ##############  ##############  ##############  ##############  ##############
    ##############  ##############  ##############  ##############  ##############  ##############  ##############
    ##############  ##############  ##############  ##############  ##############  ##############
    ############################  ##############  ##############  ##############  ##############  ##############  ##############
    ##############  ##############  ##############  ##############  ##############  ##############  ##############
    ##############  ##############  ##############  ##############  ##############  ##########################################  ##############  ##############  ##############  ##############  ##############  ##############
    ##############  ##############  ##############  ##############  ##############  ##############  ##############
    ##############  ##############  ##############  ##############  ##############  ##############
    ############################  ##############  ##############  ##############  ##############  ##############  ##############
    ##############  ##############  ##############  ##############  ##############  ##############  ##############
    ##############  ##############  ##############  ##############  ##############  ##############

    def point_of_care_update(self, email, point_of_care_list):
        """
        Replace current point of care list with submitted list.

        :param email:
        :param point_of_care:
        :return:
        """
        logger.debug("[P2M2][DEBUG][replace_point_of_care]")

        bundle_url = self.FHIR_URL

        # Retrieve patient identifier.
        patient_record = self.query_patient_record(email)
        patient_identifier = patient_record['entry'][0]['resource']['id']

        # This is a FHIR resources that allows references between resources.
        # Create one for referencing patients.
        patient_reference = FHIRReference()
        patient_reference.reference = "Patient/" + patient_identifier

        # The list will hold Organization resources representing where patients have received care.
        data_list = List()

        data_list.subject = patient_reference
        data_list.status = "current"
        data_list.mode = "working"

        # We use the SNOMED code for location to define the context of items added to the list.
        data_list.code = self.generate_snowmed_codeable(self.SNOMED_LOCATION_CODE)

        # This adds the list of Organization references.
        data_list.entry = self.generate_organization_references(point_of_care_list)

        # Start building the bundle. Bundles are used to submit multiple related resources.
        bundle_entries = []

        org_list = self.generate_organization_list(point_of_care_list)

        # Add Organization objects to bundle.
        for org in org_list:
            bundle_item_org_request = BundleEntryRequest()
            bundle_item_org_request.method = "POST"
            bundle_item_org_request.url = "Organization"

            # Don't recreate Organizations if we can find them by the exact name. No fuzzy matching.
            bundle_item_org_request.ifNoneExist = str(furl.Query({'name:exact': org.name}))

            bundle_item_org = BundleEntry()
            bundle_item_org.resource = org
            bundle_item_org.request = bundle_item_org_request

            bundle_entries.append(bundle_item_org)

        bundle_item_list_request = BundleEntryRequest()
        bundle_item_list_request.url = "List"
        bundle_item_list_request.method = "POST"
        bundle_item_list_request.ifNoneExist = str(
            furl.Query({'patient:Patient.identifier': 'http://schema.org/email|' + email,
                        'code': self.SNOMED_VERSION_URI + "|" + self.SNOMED_LOCATION_CODE,
                        'status': 'current'}))

        bundle_item_list = BundleEntry()
        bundle_item_list.resource = data_list
        bundle_item_list.request = bundle_item_list_request

        bundle_entries.append(bundle_item_list)

        # Create and send the full bundle.
        full_bundle = Bundle()
        full_bundle.entry = bundle_entries
        full_bundle.type = "transaction"

        response = requests.post(url=bundle_url, json=full_bundle.as_json())

        return response

    def generate_snowmed_codeable(self, snomed_code):
        """
        When submitting a code to fire it needs to be in a nested set of resources. This builds them based on a code and URI.
        :param snomed_code:
        :return:
        """
        snomed_coding = Coding()
        snomed_coding.system = self.SNOMED_VERSION_URI
        snomed_coding.code = snomed_code

        snomed_codable = CodeableConcept()
        snomed_codable.coding = [snomed_coding]

        return snomed_codable

    def generate_organization_list(self, point_of_care_list):
        """
        Creates Organization resources with names equal to each item in the passed in list.
        :param point_of_care_list:
        :return:
        """
        org_list = []
        org_number = 1

        for point_of_care in point_of_care_list:
            new_poc = Organization()

            new_poc.id = "org" + str(org_number)
            new_poc.name = point_of_care

            org_list.append(new_poc)
            org_number += 1

        return org_list

    def generate_organization_references(self, point_of_care_list):
        """
        When referencing resources in FHIR you need to create a reference resource.
        Create the reference for Organizations here.
        :param point_of_care_list:
        :return:
        """
        entry_list = []
        org_number = 1

        for point_of_care in point_of_care_list:
            new_org_reference = FHIRReference()
            new_org_reference.reference = "Organization/org" + str(org_number)
            new_list_entry = ListEntry()

            new_list_entry.item = new_org_reference
            entry_list.append(new_list_entry)
            org_number += 1

        return entry_list

    def query_list_record(self, email, code_system=SNOMED_VERSION_URI, code=SNOMED_LOCATION_CODE, flatten_return=False):
        """
        Query the list object which has a patient and a snomed code. If it exists we'll need the URL to update the object later.
        :param email:
        :param code_system:
        :param code:
        :return:
        """

        logger.debug("[P2M2][DEBUG][query_list_record]")

        url = self.FHIR_URL + '/List'

        query = {
            'patient:Patient.identifier': 'http://schema.org/email|' + email,
            'code': code_system + "|" + code,
            'status': 'current',
            '_include': "List:item"
        }

        response = requests.get(url, params=query)

        if flatten_return:
            response_json = flatten_list(response.json())
        else:
            response_json = response.json()

        return response_json

    def query_patient_record(self, email=None, fhir_id=None, includes=[], flatten_return=False):
        """ Get the patient record from the FHIR server.

        :param email: A patient's email address.
        :return: JSON Record of Patient
        """

        logger.debug("[P2M2][DEBUG][query_patient_record]")

        url = self.FHIR_URL + '/Patient'

        if email is not None:
            query = {
                'identifier': 'http://schema.org/email|' + email,
            }
        elif fhir_id is not None:
            query = {
                '_id': fhir_id
            }
        else:
            query = {'_count': 1000}

        # Check for includes.
        if 'enrollment' in includes:
            query.update({
                '_revinclude': 'Flag:subject',
            })
        if 'consent' in includes:
            query.update({
                '_revinclude': 'Composition:subject',
                '_include': '*'
            })
        if 'points_of_care' in includes:
            query.update({
                '_revinclude': 'List:subject',
                '_include': '*',
            })
        if 'questionnaire' in includes:
            query.update({
                '_revinclude': 'QuestionnaireResponse:source',
                '_include': '*',
            })

        # Make the request.
        response_json = requests.get(url, params=query).json()

        if flatten_return:
            response_json = flatten_participant(response_json, includes) if email is not None \
                else flatten_participants(response_json, includes)

        return response_json

    def query_questionnaire_responses(self, email=None, questionnaire_id=None, flatten_return=False):
        """
        Fetch QuestionnaireResponse and Questionnaire resources for the given patient and questionnaire ID
        :param email: The email of the user for which the Q and QRs should be fetched
        :type email: str
        :param questionnaire_id: The ID of the Questionnaire resource to fetch
        :type questionnaire_id: str
        :param flatten_return: Whether the response should be parsed and trimmed to the relevant bits
        :type flatten_return: bool
        :return: A dict of the full response or the flattened response
        :rtype: dict
        """

        logger.debug('[P2M2][DEBUG][query_questionnaire_responses] - questionnaire_id - {}'.format(questionnaire_id))

        # Build the FHIR QuestionnaireResponse URL.
        url = self.FHIR_URL + '/QuestionnaireResponse'

        # Get only "proposed" Consent resources
        query = {
            '_include': 'QuestionnaireResponse:questionnaire',
        }

        if email:
            query['source:Patient.identifier'] = 'http://schema.org/email|' + email

        if questionnaire_id:
            query['questionnaire'] = questionnaire_id

        response = requests.get(url, params=query)

        if flatten_return:
            response_json = flatten_questionnaire_response(response.json())
        else:
            response_json = response.json()

        return response_json

    def query_document_reference(self, subject=None):

        logger.debug("[P2M2][DEBUG][query_document_reference]")

        url = self.FHIR_URL + '/DocumentReference'

        query = {}

        if subject:
            query['subject'] = subject

        response = requests.get(url, params=query)

        return response.json()

    def query_user_composition(self, user_id, flatten_return=False):

        logger.debug("[P2M2][DEBUG][query_user_composition]")

        # Build the FHIR QuestionnaireResponse URL.
        url = self.FHIR_URL + '/Composition'

        query = {
            'patient': user_id,
            '_include': "*"
        }

        # Make the FHIR request.
        response = requests.get(url, params=query)

        if flatten_return:
            response_json = flatten_consent_composition(response.json(), self.FHIR_URL)
        else:
            response_json = response.json()

        return response_json

    def query_user_consent(self, email, flatten_return=False):
        """ Ask the FHIR server if this user has completed the questionnaire.

        This will return all Consent resources, with any status. If you are only
        interested in Consent resources that have been approved, filter the results
        by "status == active".
        """

        logger.debug("[P2M2][DEBUG][query_user_consent]")

        # Build the FHIR QuestionnaireResponse URL.
        url = self.FHIR_URL + '/Consent'

        # Structure the query so that we don't need to know the user's FHIR id.
        query = {
            'patient:Patient.identifier': 'http://schema.org/email|' + email,
        }

        # Make the FHIR request.
        response = requests.get(url, params=query)

        if flatten_return:
            response_json = flatten_consent(response.json())
        else:
            response_json = response.json()

        return response_json

    def query_user_contract(self, participant_email, flatten_return=False):

        logger.debug("[P2M2][DEBUG][query_user_contract]")

        # Build the FHIR QuestionnaireResponse URL.
        url = self.FHIR_URL + '/Contract'

        # Structure the query so that we don't need to know the user's FHIR id.
        query = {
            'signer:Patient.identifier': 'http://schema.org/email|' + participant_email,
        }

        # Make the FHIR request.
        response = requests.get(url, params=query)

        if flatten_return:
            return flatten_contract(response.json())
        else:
            return response.json()

    def query_guardian_contract(self, participant_email, flatten_return=False):

        logger.debug("[P2M2][DEBUG][query_guardian_contract]")

        # Build the FHIR QuestionnaireResponse URL.
        url = self.FHIR_URL + '/Contract'

        # Structure the query so that we don't need to know the user's FHIR id.
        query = {
            'signer.patient:Patient.identifier': 'http://schema.org/email|' + participant_email,
        }

        # Make the FHIR request.
        response = requests.get(url, params=query)

        if flatten_return:
            return flatten_contract(response.json())
        else:
            return response.json()

    def update_FHIR_object(self, user_consent):
        """ Send an updated consent object to the FHIR server.

        :param user_consent: Consent object as it is pulled and updated from the FHIR server.
        :return:
        """

        logger.debug("[P2M2][DEBUG][update_FHIR_object]")

        try:
            url = user_consent['fullUrl']
            user_data = user_consent['resource']

            # Make the FHIR request.
            response = requests.put(url, json=user_data)

            try:
                query_status = response.json()['text']['status']
            except (KeyError, IndexError):
                query_status = "failed"
        except (KeyError, IndexError):
            query_status = "failed"

        return query_status

    def update_user_consent(self, user_consent):
        """ Send an updated consent object to the FHIR server.

        :param user_consent: Consent object as it is pulled and updated from the FHIR server.
        :return:
        """

        logger.debug("[P2M2][DEBUG][update_user_consent]")

        try:
            url = user_consent['fullUrl']
            user_data = user_consent['resource']

            # Make the FHIR request.
            response = requests.put(url, json=user_data)

            try:
                query_status = response.json()['text']['status']
            except (KeyError, IndexError):
                query_status = "failed"
        except (KeyError, IndexError):
            query_status = "failed"

        return query_status

    def query_patients_by_enrollment(self, enroll_status):

        # Build the FHIR URL.
        url = furl.furl(self.FHIR_URL)
        url.path.segments.append('Flag')

        # Get all flags with the passed enroll status. Since Flag does not permit searching based
        # on 'code' or 'status' or any other relevant property, we will search based on the whole
        # text description of the resource. This is shaky at best.
        # TODO: Hopefully optimize this with a more concrete method of querying
        query = {
            '_content': enroll_status,
            '_include': 'Flag:patient',
        }

        response = requests.get(url.url, params=query)

        # Setup a list to hold Patient resources.
        patients = []
        try:
            # Parse the response.
            data = response.json()
            if 'entry' in data and len(data['entry']) > 0:
                # Filter out Flags.
                patients = [entry for entry in data['entry'] if entry['resource']['resourceType'] == 'Patient']

        except Exception as e:
            logger.exception("[P2M2][DEBUG][query_enrollment_status] Exception: {}".format(e))

        finally:
            return patients

    def query_enrollment_flag(self, email, flatten_return=False):

        logger.debug("[P2M2][DEBUG][query_enrollment_flag]")

        # Build the FHIR Consent URL.
        url = self.FHIR_URL + '/Flag'

        # Get flags for current user
        query = {
            'subject:Patient.identifier': 'http://schema.org/email|' + email
        }

        try:
            # Make the FHIR request.
            response = requests.get(url, params=query)

            if flatten_return:
                return flatten_enrollment_flag(response.json())
            else:
                return response.json()

        except KeyError as e:
            logger.exception('[P2M2][EXCEPTION][query_enrollment_flag]: {}'.format(e))

            raise

    def query_enrollment_status(self, email):

        logger.debug("[P2M2][DEBUG][query_enrollment_status]")

        try:
            # Make the FHIR request.
            response = self.query_enrollment_flag(email)

            # Parse the bundle.
            bundle = Bundle(response)
            if bundle.total > 0:

                # Check flags.
                for flag in [entry.resource for entry in bundle.entry if entry.resource.resource_type == 'Flag']:
                    # Get the code's value
                    state = flag.code.coding[0].code
                    logger.debug("[P2M2][DEBUG][query_enrollment_status] Fetched state '{}' for user".format(state))

                    return state

            else:

                logger.debug("[P2M2][DEBUG][query_enrollment_status] No flag found for user")

            return None

        except KeyError as e:
            logger.exception('[P2M2][EXCEPTION][query_enrollment_status]: {}'.format(e))

            raise

    def query_consents_by_status(self, status):
        """
        Ask the FHIR server for any Consent resources still pending.
        :param status:
        :return:
        """

        logger.debug("[P2M2][DEBUG][query_consents_by_status]")

        # Build the FHIR Consent URL.
        url = self.FHIR_URL + '/Consent'

        # Get only "proposed" Consent resources
        query = {
            'status': status,
            '_include': 'Consent:patient',
        }

        # Make the FHIR request.
        response = requests.get(url, params=query)

        return response.json()

    def query_questionnaire_response_by_status(self, status, questionnaire):
        """
        Ask the FHIR server for any Questionnaire resources still pending.
        :param status: The status of the response
        :param questionnaire: The FHIR id of the questionnaire the responses belong to
        :return:
        """

        logger.debug("[P2M2][DEBUG][query_questionnaire_response_by_status]")

        # Build the FHIR Consent URL.
        url = self.FHIR_URL + '/QuestionnaireResponse'

        # Get only "proposed" Consent resources
        query = {
            'status': status,
            'questionnaire': questionnaire,
            '_include': 'QuestionnaireResponse:source',
        }

        # Make the FHIR request.
        response = requests.get(url, params=query)

        return response.json()

    def create_user_in_fhir_server(self, form):
        """
        Create a Patient resource in the FHIR server.
        :param form:
        :return:
        """

        logger.debug("[P2M2][DEBUG][create_user_in_fhir_server]")

        # Build a FHIR-structured Patient resource.
        patient_data = {
            'resourceType': 'Patient',
            'identifier': [
                {
                    'system': 'http://schema.org/email',
                    'value': form.get('email'),
                },
            ],
            'name': [
                {
                    'use': 'official',
                    'family': form.get('lastname'),
                    'given': [form.get('firstname')],
                },
            ],
            'address': [
                {
                    'line': [
                        form.get('street_address1'),
                        form.get('street_address2'),
                    ],
                    'city': form.get('city'),
                    'postalCode': form.get('zip'),
                    'state': form.get('state'),
                }
            ],
            'telecom': [
                {
                    'system': 'phone',
                    'value': form.get('phone'),
                },
            ],
        }

        # Convert the twitter handle to a URL
        if form.get('twitter_handle'):
            patient_data['telecom'].append({
                'system': 'other',
                'value': 'https://twitter.com/' + form['twitter_handle'],
            })

        try:

            # Create a placeholder ID for the patient the flag can reference.
            patient_id = uuid.uuid1().urn

            # Use the FHIR client lib to validate our resource.
            # "If-None-Exist" can be used for conditional create operations in FHIR.
            # If there is already a Patient resource identified by the provided email
            # address, no duplicate records will be created.
            Patient(patient_data)

            patient_request = BundleEntryRequest({
                'url': 'Patient',
                'method': 'POST',
                'ifNoneExist': str(furl.Query({
                    'identifier': 'http://schema.org/email|' + form.get('email'),
                }))
            })
            patient_entry = BundleEntry({
                'resource': patient_data,
                'fullUrl': patient_id
            })
            patient_entry.request = patient_request

            # Validate.
            flag = Flag(fhir_resources.enrollment_flag(patient_id, 'registered'))
            flag_request = BundleEntryRequest({'url': 'Flag', 'method': 'POST'})
            flag_entry = BundleEntry({'resource': flag.as_json()})
            flag_entry.request = flag_request

            # Validate it.
            bundle = Bundle()
            bundle.entry = [patient_entry, flag_entry]
            bundle.type = 'transaction'

            logger.debug("[P2M2][DEBUG][create_user_in_fhir_server]")

            # Create the Patient and Flag on the FHIR server.
            # If we needed the Patient resource id, we could follow the redirect
            # returned from a successful POST operation, and get the id out of the
            # new resource. We don't though, so we can save an HTTP request.
            requests.post(self.FHIR_URL, json=bundle.as_json())

        except Exception as e:
            logger.exception("[P2M2][DEBUG][create_user_in_fhir_server] Exception: {}".format(e))
            raise

    def attach_json_to_participant_record(self, patient_id, json_blob, json_description):
        """

        :param patient_id:
        :param json_blob:
        :param json_description:
        :return:
        """

        logger.debug("[P2M2][DEBUG][attach_json_to_participant_record]")

        encoded_json = base64.b64encode(json.dumps(json_blob).encode()).decode('utf-8')

        data = {
            'resourceType': 'DocumentReference',
            "subject": {
                "reference": "Patient/" + patient_id
            },
            "type": {
                "text": json_description
            },
            "status": "current",
            "content": [{
                "attachment": {
                    "contentType": "application/json",
                    "language": "en-US",
                    "data": encoded_json
                }
            }]
        }

        url = self.FHIR_URL + "/DocumentReference"
        requests.post(url, json=data)

    def update_twitter_handle(self, email, twitter_handle):
        """

        :param email:
        :param twitter_handle:
        :return:
        """

        logger.debug("[P2M2][DEBUG][update_twitter_handle]")

        found_twitter_entry = False

        current_participant_record = self.query_patient_record(email)['entry'][0]

        for telecom in current_participant_record['resource']['telecom']:
            if telecom['system'] == "other" and telecom['value'].startswith("https://twitter.com"):
                telecom['value'] = 'https://twitter.com/' + twitter_handle
                found_twitter_entry = True

        if not found_twitter_entry:
            current_participant_record['resource']['telecom'].append({
                'system': 'other',
                'value': 'https://twitter.com/' + twitter_handle,
            })

        self.update_FHIR_object(current_participant_record)

    def twitter_handle_from_bundle(self, participant_bundle):
        """

        :param participant_bundle:
        :return:
        """

        logger.debug("[P2M2][DEBUG][twitter_handle_from_bundle]")

        try:
            for telecom in participant_bundle['resource']['telecom']:
                if telecom['system'] == "other" and telecom['value'].startswith("https://twitter.com"):
                    return telecom['value']
        except (KeyError, IndexError):
            print("Twitter Handle not found where expected.")

        return None

    def update_patient_enrollment(self, patient_id, status):

        logger.debug("[P2M2][DEBUG][update_patient_enrollment]")

        # Fetch the flag.
        url = furl.furl(self.FHIR_URL)
        url.path.segments.append('Flag')

        query = {
            'subject': 'Patient/{}'.format(patient_id),
        }

        try:
            # Fetch the flag.
            response = requests.get(url.url, params=query)
            flag_entries = Bundle(response.json())

            # Check for nothing.
            if flag_entries.total == 0:

                # Create it.
                return self.create_patient_enrollment('Patient/{}'.format(patient_id), status)

            else:
                # Get the first and only flag.
                entry = flag_entries.entry[0]
                flag = entry.resource
                code = flag.code.coding[0]

                # Update flag properties for particular states.
                if code.code != 'accepted' and status == 'accepted':

                    # Set status.
                    flag.status = 'active'

                    # Set a start date.
                    now = FHIRDate(datetime.now().isoformat())
                    period = Period()
                    period.start = now
                    flag.period = period

                elif code.code != 'terminated' and status == 'terminated':

                    # Set status.
                    flag.status = 'inactive'

                    # Set an end date.
                    now = FHIRDate(datetime.now().isoformat())
                    flag.period.end = now

                else:

                    # Flag defaults to inactive with no start or end dates.
                    flag.status = 'inactive'
                    flag.period = None

                # Set the code.
                code.code = status
                code.display = status.title()
                flag.code.text = status.title()

                logger.debug('[P2M2][DEBUG][update_patient_enrollment]: Updating Flag "{}" with code: "{}"'
                             .format(entry.fullUrl, status))

                # Post it.
                return requests.put(entry.fullUrl, json=flag.as_json())

        except Exception as e:
            logger.exception('[P2M2][EXCEPTION][update_patient_enrollment]: {}'.format(e))
            raise

    def create_patient_enrollment(self, patient_id, status='registered'):
        """
        Create a Flag resource in the FHIR server to indicate a user's enrollment.
        :param patient_id:
        :param status:
        :return:
        """

        logger.debug("[P2M2][DEBUG][create_enrollment_flag_for_patient]")

        # Use the FHIR client lib to validate our resource.
        flag = Flag(fhir_resources.enrollment_flag(patient_id, status))

        # Set a date if enrolled.
        if status == 'accepted':
            now = FHIRDate(datetime.now().isoformat())
            period = Period()
            period.start = now
            flag.period = period

        # Build the FHIR Flag destination URL.
        url = furl.furl(self.FHIR_URL)
        url.path.segments.append('Flag')

        logger.debug("[P2M2][DEBUG][create_enrollment_flag_for_patient] " + url.url)

        response = requests.post(url.url, json=flag.as_json())

        return response

    def remove_patient(self, participant_email):
        patient_json = self.query_patient_record(participant_email)

        try:
            patient_id_to_remove = patient_json['entry'][0]['resource']['id']
        except (KeyError, IndexError):
            logger.debug("[P2M2][DEBUG][remove_patient] - Could not find patient to remove.")
            return

        # Build the FHIR Patient URL.
        url = self.FHIR_URL + '/Patient/' + patient_id_to_remove

        # Make the FHIR request.
        response = requests.delete(url)

        return response

    def remove_consent(self, participant_email):

        # We could search by e-mail, but let's grab the participant subject ID here.
        participant_info = self.query_patient_record(participant_email, True)

        # Composition is what we package the consents in. Need to delete it before deleting consent.
        composition_json = self.query_user_composition(participant_info["fhir_id"], flatten_return=False)

        # Grab the consent to remove.
        consent_json = self.query_user_consent(participant_email)

        # Get the contract.
        contract_json = self.query_user_contract(participant_email)

        try:
            composition_id_to_remove = composition_json['entry'][0]['resource']['id']

            # Delete composition record.
            requests.delete(self.FHIR_URL + '/Composition/' + composition_id_to_remove)

        except (KeyError, IndexError):
            logger.debug("[P2M2][DEBUG][remove_consent] - Could not find composition to remove.")

        try:
            consent_id_to_remove = consent_json['entry'][0]['resource']['id']

            # Delete consent record.
            requests.delete(self.FHIR_URL + '/Consent/' + consent_id_to_remove)

        except (KeyError, IndexError):
            logger.debug("[P2M2][DEBUG][remove_consent] - Could not find consent to remove.")
            return

        try:
            contract_id_to_remove = contract_json['entry'][0]['resource']['id']

            # Delete contract record.
            requests.delete(self.FHIR_URL + '/Contract/' + contract_id_to_remove)

        except (KeyError, IndexError):
            logger.debug("[P2M2][DEBUG][remove_consent] - Could not find contract to remove.")
            return

        # Check for guardian contracts.
        guardian_contract_json = self.query_guardian_contract(participant_email)
        if guardian_contract_json.get('entry'):
            for contract in guardian_contract_json['entry']:

                # Get the id.
                try:
                    contract_id_to_remove = contract['resource']['id']

                    # Do the delete.
                    requests.delete(self.FHIR_URL + '/Contract/' + contract_id_to_remove)

                except (KeyError, IndexError):
                    logger.debug("[P2M2][DEBUG][remove_consent] - Could not find guardian contract to remove.")

        return

    def remove_point_of_care_list(self, participant_email):
        list_record = self.query_list_record(participant_email)
        try:
            for list_entry in list_record["entry"]:
                if list_entry['resource']['resourceType'] == "List":
                    url = self.FHIR_URL + '/List/' + list_entry['resource']['id']
                    requests.delete(url)
        except (KeyError, IndexError):
            logger.debug("[P2M2][DEBUG][remove_point_of_care_list] - Could not find POC.")
            return
        return

    def remove_consent_response(self, participant_email, questionnaire_id):

        consent_responses = self.query_questionnaire_responses(participant_email, questionnaire_id)
        try:
            for response_consent in consent_responses["entry"]:
                url = self.FHIR_URL + '/QuestionnaireResponse/' + response_consent['resource']['id']
                requests.delete(url)
        except (KeyError, IndexError):
            logger.debug("[P2M2][DEBUG][remove_consent_response] - Could not find consent response to "
                         "remove for questionnaire ID: {}.".format(questionnaire_id))
            return

    def remove_questionnaire(self, participant_email, questionnaire_id):

        questionnaire_responses = self.query_questionnaire_responses(participant_email, questionnaire_id)
        try:
            for questionnaire_response in questionnaire_responses["entry"]:
                if questionnaire_response['resource']['resourceType'] == "QuestionnaireResponse":
                    url = self.FHIR_URL + '/QuestionnaireResponse/' + questionnaire_response['resource']['id']
                    requests.delete(url)
        except (KeyError, IndexError):
            logger.debug("[P2M2][DEBUG][remove_questionnaire] - Could not find questionnaire to "
                         "remove for ID: {}.".format(questionnaire_id))
            return
        return

    def remove_enrollment_flag(self, participant_email):

        flag = self.query_enrollment_flag(participant_email)
        try:
            url = self.FHIR_URL + '/Flag/' + flag['entry'][0]['resource']['id']
            requests.delete(url)
        except (KeyError, IndexError):
            logger.debug("[P2M2][DEBUG][remove_enrollment_flag] - Could not find enrollment flag to remove.")
            return
        return


def get_or(item, keys, default=''):
    '''
    Fetch a property from a json object. Keys is a list of keys and indices to use to
    fetch the property. Returns the passed default string if the path through the json
    does not exist.
    :param item: The json to parse properties from
    :type item: json object
    :param keys: The list of keys and indices for the property
    :type keys: A list of string or int
    :param default: The default string to use if a property could not be found
    :type default: String
    :return: The requested property or the default value if missing
    :rtype: String
    '''
    try:
        # Try it out.
        for key in keys:
            item = item[key]

        return item
    except (KeyError, IndexError):
        return default


def get_resource(json, type=None, index=0):
    '''
    This method gets the resource json object from a search or bundle or individual response
    from FHIR. If multple resource records exist in the given json object, return the one
    at the passed index, by default the first one. Returns None if a valid resource object
    could not be found.
    :param json: The response json from FHIR
    :type json: json
    :param index: The index of the resource to return if multiple are found
    :type index: integer
    :return: The json resource object
    :rtype: json
    '''
    try:
        # Check for a single item.
        if json.get('resource', None):
            return json['resource']

        # Check for a bundle.
        elif json.get('entry', None):

            # Get the list.
            list = json['entry']

            # Check type.
            if type:

                # Filter the resource types out.
                resources = [item['resource'] for item in list if item['resource']['resourceType'] == type]

                # Check results.
                if len(resources) == 1:
                    return resources[0]

                elif len(resources) > 1 and len(resources) > index:
                    return resources[index]

                else:
                    return None

            else:

                # Check the index.
                if index < len(list):
                    return list[index]['resource']

        # Check for already a resource.
        elif json.get('id', None) and json.get('resourceType', None):
            return json

    except Exception as e:
        print('Exception: {}'.format(e))

    return None


def get_resources(json, type=None):
    '''
    This method gets the resource json objects from a search or bundle or individual response
    from FHIR. Returns a list with all discovered resource objects. Returns [] if no valid resource objects
    could be found.
    :param json: The response json from FHIR
    :type json: json
    :return: A list of json resource objects
    :rtype: [json]
    '''
    try:
        # Check type.
        if type(json) is dict:

            # Check the resource type.
            resource_type = json.get('resourceType', None)
            if resource_type == 'Bundle':

                # Check number of results.
                if json.get('total', 0) > 0:

                    # Get the list depending on type.
                    if type:
                        resources = [entry['resource'] for entry in json['entry']
                                     if entry['resource']['resourceType'] == type]
                    else:
                        resources = [entry['resource'] for entry in json['entry']]

                    return resources

            elif resource_type is not None:

                # Is a single item.
                if type is None or resource_type == type:
                    return [json]

            elif json.get('resource'):

                # Item is a single search result resource
                if type is None or type == json['resource']['resourceType']:
                    return [json.get('resource')]

        elif type(json) is list and len(json) > 0:

            # Check for a search's results.
            if json[0].get('resource'):

                resources = [entry['resource'] for entry in json if entry.get('resource')]

                return resources

            elif json[0].get('resourceType'):

                # This is already a list of resources.
                return json

    except Exception as e:
        print('Exception: {}'.format(e))

    return []


def flatten_consent(incoming_json):
    participant_record = dict()

    participant_record["consent_start"] = incoming_json['entry'][0]['resource']['period']['start']
    participant_record["status"] = incoming_json['entry'][0]['resource']['status']

    return participant_record


def flatten_questionnaire_response(incoming_json):
    """
    Flatten FHIR resources containing a questionnaire and its responses.
    :param incoming_json: The FHIR response containing at least one Questionnaire
    and one QuestionnaireResponse resources
    :type incoming_json: dict
    :return: A dict keyed by the questions of the Questionnaire and the values being
    a list of answers.
    :rtype: dict
    """

    response = {}

    # Get the resources
    q_resource = next(resource['resource'] for resource in incoming_json['entry']
                      if resource['resource']['resourceType'] == 'Questionnaire')
    a_resource = next(resource['resource'] for resource in incoming_json['entry']
                      if resource['resource']['resourceType'] == 'QuestionnaireResponse')

    # Get each question.
    for question_index, question in enumerate([item for item in q_resource.get('item', [])
                                               if item.get('linkId') is not None], 1):

        # Append the index to the question.
        question_text = '{}. {}'.format(question_index, question['text'])

        # Initialize the question's key-value pair.
        response[question_text] = []

        # Get all answers.
        answers = [response for response in a_resource['item']
                   if question['linkId'] == response['linkId']]

        # Find all answers.
        for answer_index, answer in enumerate(answers, 1):

            # Get the question type.
            if question.get('type') == 'boolean':

                # Get the text of the answer.
                answer_value = 'True' if answer['answer'][0]['valueString'] == '1' else 'False'

            else:

                # Get the text of the answer.
                answer_value = answer['answer'][0]['valueString']

            # Check for a sub-answer.
            sub_answer = next((item['answer'][0]['valueString'] for item in a_resource.get('item', [])
                               if item['linkId'] == '{}-{}'.format(question['linkId'], answer_index)), None)
            if sub_answer is not None:
                # Add it.
                answer_value += ' ({})'.format(sub_answer)

            # Add it.
            response[question_text].append(answer_value)

    return response


def flatten_consent_composition(incoming_json, fhir_url):
    incoming_bundle = Bundle(incoming_json)

    # Prepare the object.
    consent_object = {
        'consent_questionnaires': [],
        'assent_questionnaires': [],
    }
    consent_exceptions = []
    assent_exceptions = []

    if incoming_bundle.total > 0:

        for bundle_entry in incoming_bundle.entry:
            if bundle_entry.resource.resource_type == "Consent":

                signed_consent = bundle_entry.resource

                # We can pull the date from the Consent Resource. It's stamped in a few places.
                consent_object["date_signed"] = signed_consent.dateTime.origval

                # Exceptions are for when they refuse part of the consent.
                if signed_consent.except_fhir:
                    for consent_exception in signed_consent.except_fhir:
                        consent_exceptions.append(consent_exception.code[0].display)

            elif bundle_entry.resource.resource_type == 'Composition':

                composition = bundle_entry.resource

                entries = [section.entry for section in composition.section if section.entry is not None]
                references = [entry[0].reference for entry in entries if
                              len(entry) > 0 and entry[0].reference is not None]
                text = [section.text.div for section in composition.section if section.text is not None][0]

                # Check the references for a Consent object, making this comp the consent one.
                if len([r for r in references if 'Consent' in r]) > 0:
                    consent_object['consent_text'] = text
                else:
                    consent_object['assent_text'] = text

            elif bundle_entry.resource.resource_type == "RelatedPerson":
                pass
            elif bundle_entry.resource.resource_type == "Contract":

                contract = bundle_entry.resource

                # Contracts with a binding reference are either the individual consent or the guardian consent.
                if contract.bindingReference:

                    # Fetch the questionnaire and its responses.
                    url = fhir_url + "/QuestionnaireResponse/"
                    params = {
                        '_id': re.search('[^\/](\d+)$', contract.bindingReference.reference).group(0),
                        '_include': 'QuestionnaireResponse:questionnaire'
                    }
                    r = requests.get(url, params=params)
                    r.raise_for_status()

                    # Add link IDs.
                    json = inject_link_ids(r.json())

                    # Parse out the request.
                    questionnaire_bundle = Bundle(json)

                    # Get the questionnaire and its response.
                    questionnaire = [entry.resource for entry in questionnaire_bundle.entry if
                                     entry.resource.resource_type == 'Questionnaire'][0]
                    questionnaire_response = [entry.resource for entry in questionnaire_bundle.entry if
                                              entry.resource.resource_type == 'QuestionnaireResponse'][0]

                    # The reference refers to a Questionnaire which is linked to a part of the consent form.
                    if questionnaire_response.questionnaire.reference == "Questionnaire/individual-signature-part-1" \
                            or questionnaire_response.questionnaire.reference == "Questionnaire/neer-signature":

                        # This is a person consenting for themselves.
                        consent_object["type"] = "INDIVIDUAL"
                        consent_object["signor_signature"] = base64.b64decode(contract.signer[0].signature[0].blob)
                        consent_object["participant_name"] = contract.signer[0].signature[0].whoReference.display

                        # These don't apply on an Individual consent.
                        consent_object["participant_acknowledgement_reason"] = "N/A"
                        consent_object["participant_acknowledgement"] = "N/A"
                        consent_object["signor_name"] = "N/A"
                        consent_object["signor_relationship"] = "N/A"
                        consent_object["assent_signature"] = "N/A"
                        consent_object["assent_date"] = "N/A"
                        consent_object["explained_signature"] = "N/A"

                    elif questionnaire_response.questionnaire.reference == "Questionnaire/guardian-signature-part-1":

                        # This is a person consenting for someone else.
                        consent_object["type"] = "GUARDIAN"

                        # Get the Related Person resource who signed the contract.
                        related_person_get = requests.get(fhir_url + "/" + contract.signer[0].party.reference)
                        related_person = RelatedPerson(related_person_get.json())

                        consent_object["signor_name"] = related_person.name[0].text
                        consent_object["signor_relationship"] = related_person.relationship.text

                        consent_object["participant_name"] = contract.signer[0].signature[0].onBehalfOfReference.display
                        consent_object["signor_signature"] = base64.b64decode(contract.signer[0].signature[0].blob)

                    elif questionnaire_response.questionnaire.reference == "Questionnaire/guardian-signature-part-2":

                        # This is the question about being able to get acknowledgement from the participant by the guardian/parent.
                        consent_object["participant_acknowledgement"] = questionnaire_response.item[0].answer[
                            0].valueString

                        # If the answer to the question is no, grab the reason.
                        if consent_object["participant_acknowledgement"] == "no":
                            consent_object["participant_acknowledgement_reason"] = \
                            questionnaire_response.item[1].answer[0].valueString

                        # This is the Guardian's signature letting us know they tried to explain this study.
                        consent_object["explained_signature"] = base64.b64decode(contract.signer[0].signature[0].blob)

                    elif questionnaire_response.questionnaire.reference == "Questionnaire/guardian-signature-part-3":

                        # A contract without a reference is the assent page.
                        consent_object["assent_signature"] = base64.b64decode(contract.signer[0].signature[0].blob)
                        consent_object["assent_date"] = contract.issued.origval

                        # Append the Questionnaire Text if the response is true.
                        for current_response in questionnaire_response.item:

                            if current_response.answer[0].valueBoolean:
                                answer = \
                                [item for item in questionnaire.item if item.linkId == current_response.linkId][0]
                                assent_exceptions.append(answer.text)

                    # Prepare to parse the questionnaire.
                    questionnaire_object = {
                        'template': 'dashboard/{}.html'.format(questionnaire.id),
                        'questions': []
                    }

                    for item in questionnaire.item:

                        question_object = {
                            'type': item.type,
                        }

                        if item.type == 'display':
                            question_object['text'] = item.text

                        elif item.type == 'boolean' or item.type == 'question':
                            # Get the answer.
                            for response in questionnaire_response.item:
                                if response.linkId == item.linkId:
                                    # Process the question, answer and response.
                                    if item.type == 'boolean':
                                        question_object['text'] = item.text
                                        question_object['answer'] = response.answer[0].valueBoolean

                                    elif item.type == 'question':
                                        question_object['yes'] = item.text
                                        question_object['no'] = 'I was not able to explain this study to my child or ' \
                                                                'individual in my care who will be participating'
                                        question_object['answer'] = response.answer[0].valueString is 'yes'

                        # Add it.
                        questionnaire_object['questions'].append(question_object)

                        # Check the type.
                if questionnaire_response.questionnaire.reference == "Questionnaire/guardian-signature-part-3":
                    consent_object['assent_questionnaires'].append(questionnaire_object)
                else:
                    consent_object['consent_questionnaires'].append(questionnaire_object)

    consent_object["exceptions"] = consent_exceptions
    consent_object["assent_exceptions"] = assent_exceptions

    return consent_object


def inject_link_ids(json):
    # Appeases the FHIR library by ensuring question items all have linkIds, regardless of an associated answer.
    for question in [entry['resource'] for entry in json['entry']
                     if entry['resource']['resourceType'] == 'Questionnaire']:
        for item in question['item']:
            if 'linkId' not in item:
                # Assign a random string for the linkId
                item['linkId'] = "".join([random.choice("abcdefghijklmnopqrstuvwxyz1234567890") for _ in range(10)])

    return json


def flatten_participants(incoming_json, includes=[]):
    resources = get_resources(incoming_json)

    # Parse them out.
    records = []
    for resource in resources:
        # Flatten.
        records.append(flatten_participant(resource), includes)

    return records


def flatten_participant(incoming_json, includes=[]):
    resource_record = get_resource(incoming_json, 'Patient')

    participant_record = dict()

    participant_record["email"] = resource_record['identifier'][0]['value']
    participant_record["fhir_id"] = resource_record['id']

    try:
        participant_record["firstname"] = resource_record['name'][0]['given'][0]
    except (KeyError, IndexError):
        participant_record["firstname"] = ""

    try:
        participant_record["lastname"] = resource_record['name'][0]['family']
    except (KeyError, IndexError):
        participant_record["lastname"] = ""

    try:
        participant_record["street_address1"] = resource_record['address'][0]['line'][0]
    except (KeyError, IndexError):
        participant_record["street_address1"] = ""

    try:
        participant_record["street_address2"] = resource_record['address'][0]['line'][1]
    except (KeyError, IndexError):
        participant_record["street_address2"] = ""

    try:
        participant_record["city"] = resource_record['address'][0]['city']
    except (KeyError, IndexError):
        participant_record["city"] = ""

    try:
        participant_record["state"] = resource_record['address'][0]['state']
    except (KeyError, IndexError):
        participant_record["state"] = ""

    try:
        participant_record["zip"] = resource_record['address'][0]['postalCode']
    except (KeyError, IndexError):
        participant_record["zip"] = ""

    if resource_record.get('telecom'):
        for telecom in resource_record['telecom']:
            if telecom['system'] == "phone":
                try:
                    participant_record["phone"] = telecom['value']
                except (KeyError, IndexError):
                    participant_record["phone"] = ""

            if telecom['system'] == "other":
                try:
                    participant_record["twitter_handle"] = telecom['value']
                except (KeyError, IndexError):
                    participant_record["twitter_handle"] = ""
    else:
        participant_record["phone"] = ""
        participant_record["twitter_handle"] = ""

    # Check for includes.
    if 'enrollment' in includes:
        # Get flag.
        participant_record['enrollment'] = flatten_enrollment_flag(get_resource(incoming_json, 'Flag'))

    if 'consent' in includes:
        # Get consent.
        participant_record['consent'] = flatten_consent_composition(incoming_json)

    if 'points_of_care' in includes:
        # Get consent.
        participant_record['points_of_care'] = flatten_list(incoming_json)

    if 'questionnaire' in includes:
        # Get the questionnaire.
        participant_record['questionnaire'] = flatten_questionnaire_response(incoming_json)

    return participant_record


def flatten_list(incoming_json):
    points = []

    for entry in incoming_json['entry']:
        if entry['resource']['resourceType'] == "Organization":
            points.append(entry['resource']['name'])

    return points


def flatten_enrollment_flag(incoming_json):
    # Get the resource.
    resource = get_resource(incoming_json)
    if resource:
        record = dict()

        # Try and get the values
        record['enrollment'] = get_or(resource, ['code', 'coding', 0, 'code'])
        record['status'] = get_or(resource, ['status'])
        record['start'] = get_or(resource, ['period', 'start'])
        record['end'] = get_or(resource, ['period', 'end'])

        return record

    else:
        return None


def flatten_contract(incoming_json):
    # Get the resource.
    resource = get_resource(incoming_json)
    if resource:
        record = dict()

        # Try and get the values
        record['status'] = get_or(resource, ['status'])
        record['signer'] = get_or(resource, ['signer', 0, 'party', 'reference'])
        record['patient'] = get_or(resource, ['signer', 0, 'signature', 0, 'whoReference', 'reference'])
        record['when'] = get_or(resource, ['signer', 0, 'signature', 0, 'when'])
        signature_b64 = get_or(resource, ['signer', 0, 'signature', 0, 'blob'])

        try:
            # Base64 decode.
            record['signature'] = base64.b64decode(signature_b64).decode('utf-8')
        except Exception:
            record['signature'] = ''

        return record

    else:
        return None
