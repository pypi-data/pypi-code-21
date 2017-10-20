'''
{
    type: spam
    complainant: no-reply@abusix.org
    handled_on: null
    client: 2999550572
    date: 2013-04-05T22:19:05Z
    report: {
        storage: {
            type: imap
            params: [
                {key: mailbox, value: Archive/2013-04-22}
                {key: uid, value: 106108}
            ]
        }
        send_date: 2013-04-05T22:19:05Z
        received_date: 2013-04-05T22:19:05Z
        format: marf
    }
    resources: {
        incident_part: [
            {key: original-envelope-id, value: 1uoeYp-4ftuc0-In}
            {key: feedback-type, value: abuse}
        ]
        evidence_part: [
            {
                key: received
                value: from ip-178-201-130-108.unitymediagroup.de ...
            }
            {
                key: from
                value: "Clarissa Campos" <bangsld@classprod.com>
            }
        ]
        ip: [
            {
                source: incident
                version: 4
                hex: b2c9826c
                value: 178.201.130.108
            }
        ]
    }
}
'''

from ahqapiclient.resources import Resource


class Incident(Resource):

    def __init__(self, http_client):
        super(Incident, self).__init__('/incidents', http_client)

    def make_incident_doc(self):
        return {
            'client': None,
            'type': None,
            'complainant': None,
            'complaint_source': None,
            'date': None,
            'handled_on': None,
            'report': {
                'storage': {
                    'type': None,
                    'params': [],  # key, value
                },
                'format': None,
                'received_date': None,
                'send_date': None
            },
            'resources': {
                'ip': [],  # value, hex, version, source
                'incident_part': [],  # key, value
                'evidence_part': [],  # key, value
                'malware': {}  # {name: foo, checksum: bar}
            },
            "product_category": None,
            "customer_type": None,
            "brand_name": None,
            "customer_number": None,
            "resolver_data": {},
            "contract_id": None,
            "contract_data": None
        }

    def create_incident(self, client, type, complainant, complaint_source, date, handled_on,
                        report, resources, product_category, customer_type,
                        brand_name, customer_number, resolver_data, contract_id,
                        contract_data):
        return self.post(
            path=self.rurl(),
            data={
                'client': client,
                'type': type,
                'complainant': complainant,
                'complaint_source': complaint_source,
                'date': date,
                'handled_on': handled_on,
                'report': report,
                'resources': resources,
                'product_category': product_category,
                'customer_type': customer_type,
                'brand_name': brand_name,
                'customer_number': customer_number,
                'resolver_data': resolver_data,
                'contract_id': contract_id,
                'contract_data': contract_data
            }
        )

    def get_incident(self, _id):
        return self.get(path=self.rurl(_id))

    def get_incidents(self, date_from, date_to, limit=10, offset=0, query='',
                      include_handled=0, sort='date:desc', raw=False):
        return self.get(
            path=self.rurl(),
            params={
                'date_from': date_from,
                'date_to': date_to,
                'limit': limit,
                'offset': offset,
                'query': query,
                'include_handled': include_handled,
                'sort': sort,
            },
            raw=raw
        )

    def total(self, date_from, date_to):
        total = self.get_incidents(date_from, date_to, 0, 0, '', 0,
                                   'date:desc', True)

        try:
            return total.headers['x-total']
        except KeyError:
            return None
