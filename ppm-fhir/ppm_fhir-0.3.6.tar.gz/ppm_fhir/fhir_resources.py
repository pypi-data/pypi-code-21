import uuid
import random
import base64
from datetime import datetime


def enrollment_flag(patient_id, status='proposed', start=None, end=None):

    data = {
        'resourceType': 'Flag',
        'status': 'active' if status == 'accepted' else 'inactive',
        'category': {
            'coding': [{
                'system': 'http://hl7.org/fhir/flag-category',
                'code': 'admin',
                'display': 'Admin',
            }],
            'text': 'Admin'
        },
        'code': {
            'coding': [{
                'system': 'https://peoplepoweredmedicine.org/enrollment-status',
                'code': status,
                'display': status.title(),
            }],
            'text': status.title(),
        },
        "subject": {
            "reference": patient_id
        }
    }

    # Set dates if specified.
    if start:
        data['period'] = {
            'start': start.isoformat()
        }
        if end:
            data['period']['end'] = end.isoformat()

    return data


def document(patient_id, description, data):

    data = {
        'resourceType': 'DocumentReference',
        "subject": {
            "reference": "Patient/" + patient_id
        },
        "type": {
            "text": description
        },
        "status": "current",
        "content": [{
            "attachment": {
                "contentType": "application/json",
                "language": "en-US",
                "data": data
            }
        }]
    }

    return data


def patient(email, first_name, last_name, street_address1, street_address2,
            city, zip_code, state, phone, twitter=None):

    data = {
        'resourceType': 'Patient',
        'identifier': [
            {
                'system': 'http://schema.org/email',
                'value': email,
            },
        ],
        'name': [
            {
                'use': 'official',
                'family': last_name,
                'given': [first_name],
            },
        ],
        'address': [
            {
                'line': [
                    street_address1,
                    street_address2,
                ],
                'city': city,
                'postalCode': zip_code,
                'state': state,
            }
        ],
        'telecom': [
            {
                'system': 'phone',
                'value': phone,
            },
        ],
    }

    # Convert the twitter handle to a URL
    if twitter:
        data['telecom'].append({
            'system': 'other',
            'value': 'https://twitter.com/' + twitter,
        })

    return data


def organization_list(item_ids, patient_id=None):

    data = {
        "resourceType": "List",
        "id": random.randint(10, 500),
        "meta": {
            "versionId": "1",
            "lastUpdated": datetime.now().isoformat(),
        },
        "status": "current",
        "mode": "working",
        "code": {
            "coding": [{
                "system": "http://snomed.info/sct/900000000000207008",
                "code": "SNOMED:43741000"
            }]
        },
        "entry": [],
    }

    # Add the items.
    for item_id in item_ids:
        data['entry'].append({'item': {'reference': item_id}})

    # Check for patient.
    if patient_id:

        # Format it if necessary.
        if not 'Patient' in patient_id:
            patient_id = 'Patient/{}'.format(patient_id)

        # Add it.
        data['subject']["reference"] = patient_id

    return data


def contract(who, signature, guardian_id=None, questionnaire_id=random.randint(0, 500), patient_id=random.randint(10, 500)):

    data = {
        "resourceType": "Contract",
        "id": random.randint(0, 500),
        "meta": {
            "versionId": "1",
            "lastUpdated": datetime.now().isoformat(),
        },
        "status": "executed",
        "issued": datetime.now().strftime('%Y-%m-%d'),
        "signer": [
            {
                "type": {
                    "system": "http://hl7.org/fhir/ValueSet/contract-signer-type",
                    "code": "CONSENTER",
                    "display": "Consenter"
                },
                "party": {
                    "reference": "Patient/{}".format(patient_id),
                },
                "signature": [
                    {
                        "type": [
                            {
                                "system": "http://hl7.org/fhir/ValueSet/signature-type",
                                "code": "1.2.840.10065.1.12.1.7",
                                "display": "Consent Signature"
                            }
                        ],
                        "when": datetime.now().isoformat(),
                        "whoReference": {
                            "reference": "Patient/{}".format(patient_id),
                            "display": who,
                        },
                        "contentType": "text/plain",
                        "blob": base64.b64encode(signature.encode('utf-8')).decode('utf-8'),
                    }
                ]
            }
        ],
        "bindingReference": {
            "reference": "QuestionnaireResponse/{}".format(questionnaire_id)
        }
    }

    # Check for a guardian.
    if guardian_id:

        # Update the party.
        data['signer'][0]['party']['reference'] = 'RelatedPerson/{}'.format(guardian_id)

        # Update who.
        data['signer'][0]['signature'][0]['whoReference']['reference'] = 'RelatedPerson/{}'.format(guardian_id)

        # Add onBehalfOf
        data['signer'][0]['signature'][0]['onBehalfOfReference'] = {
            "reference": "Patient/{}".format(patient_id),
            "display": "Guardian Name",
        }

    return data


def consent(patient_id=random.randint(10, 500)):

    data = {
        "resourceType": "Consent",
        "id": random.randint(0, 500),
        "meta": {
            "versionId": "1",
            "lastUpdated": datetime.now().isoformat(),
        },
        "status": "proposed",
        "patient": {
            "reference": "Patient/{}".format(patient_id)
        },
        "period": {
            "start": datetime.now().strftime('%Y-%m-%d'),
        },
        "dateTime": datetime.now().strftime('%Y-%m-%d'),
        "purpose": [
            {
                "system": "http://hl7.org/fhir/v3/ActReason",
                "code": "HRESCH",
                "display": "healthcare research"
            }
        ],
        "except": [
            {
                "type": "deny",
                "code": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "225098009",
                        "display": "Collection of sample of saliva"
                    }
                ]
            },
            {
                "type": "deny",
                "code": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "284036006",
                        "display": "Equipment monitoring"
                    }
                ]
            },
            {
                "type": "deny",
                "code": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "702475000",
                        "display": "Referral to clinical trial"
                    }
                ]
            }
        ]
    }

    return data


def composition(contract_ids, consent_ids, patient_id=random.randint(10, 500)):

    data = {
        "resourceType": "Composition",
        "id": random.randint(0, 500),
        "meta": {
            "versionId": "1",
            "lastUpdated": "2017-06-26T18:36:57.000+00:00"
        },
        "status": "final",
        "type": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "83930-8",
                    "display": "Research Consent"
                }
            ]
        },
        "subject": {
            "reference": "Patient/{}".format(patient_id)
        },
        "date": "2017-06-26",
        "author": [
            {
                "reference": "Device/consent-app"
            }
        ],
        "title": "Signature",
        "section": [
            {
                "text": {
                    "status": "additional",
                    "div": "{consent text}",
                }
            },
        ]
    }

    # Add consents.
    for consent_id in consent_ids:

        data['section'].append({
            "entry": [
                {
                    "reference": "Consent/{}".format(consent_id),
                }
            ]
        })

    # Add contracts.
    for contract_id in contract_ids:

        data['section'].append({
            "entry": [
                {
                    "reference": "Contract/{}".format(contract_id),
                }
            ]
        })

    return data

def bundle(resources, url='http://localhost:8080/baseDstu3'):

    # Trim leading slash on URL.
    url = url.rstrip('/')

    data = {
        "resourceType": "Bundle",
        "id": uuid.uuid4(),
        "meta": {
            "lastUpdated": datetime.now().isoformat(),
        },
        "type": "searchset",
        "total": len(resources),
        "link": [{
            "relation": "self",
            "url": url,
        }],
        "entry": [],
    }

    # Add the resources.
    for resource in resources:

        # Get the id.
        item_id = '{}/{}'.format(resource['resourceType'], resource['id'])

        # Wrap the resource.
        formatted_resource = {
            "fullUrl": url + '/' + item_id,
            "resource": resource,
            "search": {
                "mode": "match",
            }
        }

        # Add it.
        data['entry'].append(formatted_resource)

    return data
