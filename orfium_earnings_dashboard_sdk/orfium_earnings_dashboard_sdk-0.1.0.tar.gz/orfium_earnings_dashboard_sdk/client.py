import requests
import json


class OrfiumEarningsDashboardServerError(ValueError):
    pass


class OrfiumEarningsDashboardApiError(ValueError):
    pass


class OrfiumEarningsDashboardClient(object):

    def __init__(self, endpoint='https://dashboard.orfium.com/api/v1', token=''):

        if not token:
            raise ValueError('Token can not be empty')

        self.endpoint = endpoint
        self.token = token

    def register_sale(self, sale):
        """
        A shortcut to `register_sales` for a single sale
        :param sale: A single sale. See `register_sales` for more information.
        :return: See `register_sales`.
        """
        return self.register_sales(sales=[sale, ])

    def register_sales(self, sales):
        """
        :param sales: A list of valid sales. Each sale is a dict of the following form:
            {
                'sale_id': 'Sdv24Vx'  # A unique identifier of this sale
                'asset': {
                    'asset_type': 'TRACK',  # either TRACK or ALBUM
                    'title': 'Test asset',
                    'orfium_id': 1,  # may contain orfium_id or isrc, iswc, ean, upc
                },
                'source': {
                    'channel': 'ORFIUM',  # currently either ORFIUM, YOUTUBE SOUND_RECORDING or YOUTUBE COMPOSITION
                    'id': 1,  # the id of the object on that service (Orfium ID or YouTube Asset ID)
                },
                'revenue': '5.00',  # amount in USD
                'split': {
                    'User': 1  # Key is username, value is percentage of ownership (use string repr. for decimals)
                }
            }
        :return: A tuple (created, already_existing) that counts how many sales were created & how many already existed.
            May raise an OrfiumEarningsDashboardApiError exception.
        """
        # send the request
        result = requests.post('%s/sales/insert/' % self.endpoint, data={
            'sales': json.dumps(sales),
        }, headers={
            'Authorization': 'Token %s' % self.token
        })

        if result.status_code >= 500:
            raise OrfiumEarningsDashboardServerError('A server error occurred.')

        # read response as JSON
        resp = result.json()

        if result.status_code == 200:
            return resp['info']['new_sales'], resp['info']['already_existing_sales']

        else:
            error_description = resp['error'] + '\n'

            for key in resp.get('error_info', {}).keys():

                # ignore empty errors
                if not resp['error_info'][key]:
                    continue

                # humanize
                error_description += '%s\n' % key.replace('_', ' ').title().replace(' Or', ' or')

                for error_item in resp['error_info'][key]:
                    error_description += '%s\n' % json.dumps(error_item, indent=4, sort_keys=True)

            raise OrfiumEarningsDashboardApiError(error_description)

