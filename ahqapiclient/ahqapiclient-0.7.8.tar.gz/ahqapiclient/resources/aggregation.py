from ahqapiclient.resources import Resource


class Aggregation(Resource):

    def __init__(self, http_client):
        super(Aggregation, self).__init__('/aggregations', http_client)

    def get_aggr_incidents_histogram(self, date_from, date_to, client_filter,
                                     resolution='1h'):
        '''Get incidents aggregated by date'''
        return self.get(
            path=self.rurl('incidents/histogram'),
            params={
                'date_from': date_from,
                'date_to': date_to,
                'client': client_filter,
                'resolution': resolution,
            }
        )

    def get_aggr_incidents_bytype_histogram(self, date_from, date_to,
                                            client_filter,
                                            resolution='1h', query=''):
        '''Get incidents aggregated by type'''
        return self.get(
            path=self.rurl('incidents/bytype/histogram'),
            params={
                'date_from': date_from,
                'date_to': date_to,
                'client': client_filter,
                'resolution': resolution,
                'query': query
            }
        )

    def get_aggr_incidents_bytype(self, date_from, date_to, limit=10, offset=0,
                                  sort='count:desc', query='',
                                  include_cooldown='0', infected_only='0',
                                  new_only='0', in_cooldown_before_only='0'):
        '''
        Get incident count by type
        '''

        parameters = {
            'date_from': date_from,
            'date_to': date_to,
            'limit': limit,
            'offset': offset,
            'sort': sort,
            'query': query,
            'infected_only': infected_only,
            'new_only': new_only,
            'in_cooldown_before_only': in_cooldown_before_only,
        }

        if include_cooldown is not None:
            parameters['include_cooldown'] = include_cooldown

        return self.get(
            path=self.rurl('incidents/bytype'),
            params=parameters
        )

    def get_aggr_incidents_bycomplainant(self, date_from, date_to, limit=10,
                                         offset=0, sort='count:desc',
                                         query='', include_cooldown='0',
                                         infected_only='0', new_only='0',
                                         in_cooldown_before_only='0'):
        '''
        Get incident count by complainant
        '''

        parameters = {
            'date_from': date_from,
            'date_to': date_to,
            'limit': limit,
            'offset': offset,
            'sort': sort,
            'query': query,
            'infected_only': infected_only,
            'new_only': new_only,
            'in_cooldown_before_only': in_cooldown_before_only,
        }

        if include_cooldown is not None:
            parameters['include_cooldown'] = include_cooldown

        return self.get(
            path=self.rurl('incidents/bycomplainant'),
            params=parameters
        )

    def get_aggr_incidents_byinfection(self, date_from, date_to, limit=10,
                                       offset=0, sort='count:desc',
                                       query='', include_cooldown='0',
                                       infected_only='0', new_only='0',
                                       in_cooldown_before_only='0'):
        '''
        Get incident count by infection/malware
        '''

        parameters = {
            'date_from': date_from,
            'date_to': date_to,
            'limit': limit,
            'offset': offset,
            'sort': sort,
            'query': query,
            'infected_only': infected_only,
            'new_only': new_only,
            'in_cooldown_before_only': in_cooldown_before_only,
        }

        if include_cooldown is not None:
            parameters['include_cooldown'] = include_cooldown

        return self.get(
            path=self.rurl('incidents/byinfection'),
            params=parameters
        )

    def get_aggr_incidents_stats(self, date_from, date_to, query=''):
        '''Get incidents statistic'''
        return self.get(
            path=self.rurl('incidents/stats'),
            params={
                'date_from': date_from,
                'date_to': date_to,
                'query': query
            }
        )

    def get_aggr_incidents_byclient(self, date_from, date_to, limit=10,
                                    offset=0, sort='unhandled:desc', query=''):
        '''
        Get incident count by client
        '''
        return self.get(
            path=self.rurl('incidents/byclient'),
            params={
                'date_from': date_from,
                'date_to': date_to,
                'limit': limit,
                'offset': offset,
                'sort': sort,
                'query': query
            }
        )

    def get_incidents_byclient_detailed(self, date_from, date_to, limit=10,
                                        offset=0, sort='unhandled:desc',
                                        query='', include_cooldown='0',
                                        infected_only='0', new_only='0',
                                        in_cooldown_before_only='0'):
        params = {
            'date_from': date_from,
            'date_to': date_to,
            'limit': limit,
            'offset': offset,
            'query': query,
            'sort': sort,
        }

        if include_cooldown is not None:
            params['include_cooldown'] = include_cooldown

        return self.get(
            path=self.rurl('incidents/byclient/detailed'), params=params,
        )

    def get_infections(self, date_from, date_to, limit=10, offset=0,
                       client='', query='', sort=None, include_cooldown='0',
                       infected_only='0', new_only='0',
                       in_cooldown_before_only='0'):

        params = {
            'date_from': date_from,
            'date_to': date_to,
            'limit': limit,
            'offset': offset,
            'client': client,
            'query': query,
            'sort': sort,
            'infected_only': infected_only,
            'new_only': new_only,
            'in_cooldown_before_only': in_cooldown_before_only
        }

        if include_cooldown is not None:
            params['include_cooldown'] = include_cooldown

        return self.get(
            path=self.rurl('infections'), params=params,
        )

    def get_aggr_incidents_bynetworktag(self, date_from, date_to,
                                        sort='count:desc', query='',
                                        include_cooldown='0',
                                        infected_only='0', new_only='0',
                                        in_cooldown_before_only='0'):
        '''
        Get incident count by network tag
        '''

        parameters = {
            'date_from': date_from,
            'date_to': date_to,
            'sort': sort,
            'query': query,
            'infected_only': infected_only,
            'new_only': new_only,
            'in_cooldown_before_only': in_cooldown_before_only,
        }

        if include_cooldown is not None:
            parameters['include_cooldown'] = include_cooldown

        return self.get(
            path=self.rurl('incidents/bynetworktag'),
            params=parameters
        )

    def get_ip_summary(self, date_from, date_to, limit=10, client='', query='',
                       sort=None):
        params = {
            'date_from': date_from,
            'date_to': date_to,
            'limit': limit,
            'client': client,
            'query': query,
            'sort': sort
        }
        return self.get(
            path=self.rurl('ipsummary'), params=params,
        )

    def get_aggr_incidents_network_tags(self, date_from, date_to, limit=10,
                                        offset=0, query='', sort=None):
        params = {
            'date_from': date_from,
            'date_to': date_to,
            'limit': limit,
            'offset': offset,
            'query': query,
            'sort': sort
        }
        return self.get(
            path=self.rurl('incidents/networktags'), params=params,
        )
