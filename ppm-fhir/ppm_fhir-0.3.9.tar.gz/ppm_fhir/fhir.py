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

from ppm_fhir.fhir_response_processing import (flatten_consent,
                                                flatten_participants,
                                                flatten_questionnaire_response,
                                                flatten_participant,
                                                flatten_list,
                                                flatten_consent_composition,
                                                flatten_enrollment_flag,
                                               flatten_contract)
from ppm_fhir import fhir_resources

import requests
import furl
import base64
import json
from datetime import datetime
import uuid

import logging
logger = logging.getLogger(__name__)


class PPMFHIR:

    FHIR_URL = None

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

    AUTISM = 'autism'
    NEER = 'neer'
    QUESTIONNAIRE_IDS = (
        ('autism', 'asd'),
        ('neer', 'registration-information-for-ppm2'),
    )

    # Set the resource names for FHIR resources
    PATIENT = 'Patient'
    FLAG = 'Flag'
    COMPOSITION = 'Composition'
    QUESTIONNAIRE = 'Questionnaire'
    QUESTIONNAIRE_RESPONSE = 'QuestionnaireResponse'
    LIST = 'List'
    ORGANIZATION = 'Organization'

    RESOURCE_TYPES = (
        PATIENT, FLAG, COMPOSITION, QUESTIONNAIRE, QUESTIONNAIRE_RESPONSE, LIST, ORGANIZATION,
    )

    def __init__(self, fhir_url):
        self.FHIR_URL = fhir_url

    def _fhir_url(self, resource_type, query=None):
        """
        Get a valid FHIR url for the passed resource and query if needed
        :param resource_type: The FHIR resource
        :param query: A dict of query key value pairs
        :return: A FHIR url
        """

        # Ensure it is valid.
        if resource_type not in PPMFHIR.RESOURCE_TYPES:
            raise RuntimeError('"{}" is not a valid FHIR resource'.format(resource_type))

        # Build it.
        url = furl.furl(self.FHIR_URL)

        # Add the resource.
        url.path.add(resource_type)

        # Add the query
        if query is not None:
            url.query.params.update(query)

        return url.url

    def _get_resource(self, url, query=None, count=None, flattener=None):
        """
        Get the FHIR resources. Will page results and collect everything if necessary.
        :param url: The URL to query
        :param query: A dict of query key value pairs, if needed
        :param count: The number of results to return. If none, will iterate through all pages and collect
        everything
        :param flattener: A method used to flatten the resource into an appropriate dict
        :return: A list of dict resources
        """

        # Collect returned resources
        resources = []

        # Iterate through pages
        while url is not None:

            # Make the query
            response = requests.get(url, params=query)
            response.raise_for_status()

            # Parse the bundle.
            bundle = response.json()
            for entry in bundle.get('entry'):

                # Only process Patient resources
                if entry['resource']['resourceType'] == 'Patient':
                    patients.append(flatten_patient(entry['resource']))

            # Check for a page.
            url = None
            for link in bundle.get('link', []):
                if link['relation'] == 'next':
                    url = link['url']

        return patients

    def get_patient(self, email=None, fhir_id=None, flatten_return=False):
        """ Get the patient record from the FHIR server.

        :param email: A patient's email address.
        :param fhir_id: A patient's internal FHIR ID.
        :return: JSON Record of Patient
        """

        logger.debug("[PPMFHIR][DEBUG][get_patient]")

        # Determine the query
        if email is not None:
            query = {
                'identifier': 'http://schema.org/email|' + email,
            }
        elif fhir_id is not None:
            query = {
                '_id': fhir_id,
            }

        else:
            query = {'_count': 1000}

        response_json = requests.get(self._fhir_url(), params=query).json()

        if flatten_return:
            response_json = flatten_participant(response_json) if (email or fhir_id) is not None \
                else flatten_participants(response_json)

        return response_json

