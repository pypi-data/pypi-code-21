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

                # When the sale was created (optional, defaults to current time), use a datetime object
                'created': datetime.datetime(2017, 11, 1, 20, 55, tzinfo=pytz.utc),

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

        # encode the `created` time parameter
        for sale in sales:
            if 'created' in sale:
                sale['created'] = sale['created'].strftime('%Y-%m-%dT%H:%M:%SZ')

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

    def register_earnings_info(self, earnings_info):
        """
        :param earnings_info: A list of valid additional earnings info objects.
        Each earnings info is a dict of the following form:
            {
                'earnings_info_id': 'x52kj-4231',  # A unique identifier for the additional earnings info
                'user': 'User',  # Related (Orfium) username

                # Related timestamp (optional, defaults to current time), use a datetime object
                'created': datetime.datetime(2017, 11, 1, 20, 55, tzinfo=pytz.utc),

                'dimension': 'YOUTUBE_VIDEO',  # The reported dimension (currently only YOUTUBE_VIDEO supported)
                'value': 'xxxxx',  # Reference value (e.g the YouTube Video ID for YOUTUBE_VIDEO)
                'gross_earnings': "1.00",  # in USD
                'transaction_costs': "0.00",  # in USD
                'net_earnings': "0.80",  # in USD
                'info': {
                    'title': 'An awesome video'  # Video title is required for the YOUTUBE_VIDEO dimension
                    # Other info may be posted here as well
                }
            }]),
            }
        :return: A tuple (created, already_existing) that counts how many additional info
        were created & how many already existed.
            May raise an OrfiumEarningsDashboardApiError exception.
        """

        # encode the `created` time parameter
        for info in earnings_info:
            if 'created' in info:
                info['created'] = info['created'].strftime('%Y-%m-%dT%H:%M:%SZ')

        # send the request
        result = requests.post('%s/earnings-info/insert/' % self.endpoint, data={
            'earnings_info': json.dumps(earnings_info),
        }, headers={
            'Authorization': 'Token %s' % self.token
        })

        if result.status_code >= 500:
            raise OrfiumEarningsDashboardServerError('A server error occurred.')

        # read response as JSON
        resp = result.json()

        if result.status_code == 200:
            return resp['info']['new_earnings_info'], resp['info']['already_existing_earnings_info']

        else:
            error_description = ''

            err = resp.get('error', {})

            if type(err) in [str, unicode]:
                error_description = err
            else:
                for key in err:

                    # ignore empty errors
                    if not err:
                        continue

                    # humanize
                    error_description += '%s: %s\n' % (key.replace('_', ' ').title(), resp['error'][key])

            raise OrfiumEarningsDashboardApiError(error_description)
