import json


class BulkApiMixin(object):
    """Mixin class which encapsulates the functionality of the bulk API
    service.

    All the methods of this class are made available in the
    [[SquirroClient]] class.

    {TOC}
    """

    def new_shim(self, config):
        """Register a new shim with the bulk API. If the corresponding
        configuration has already been registered the corresponding identifier
        is returned instead.

        :param config: Shim configuration dictionary.
        :returns: A dictionary which contains the shim identifier.

        Example::

            >>> config = {'ext': {'user_id': '005E0000001NSP0IAO'},
                 'name': 'Salesforce Integration Shim',
                 'type': 'my-shim-type',
                 'squirro': {'projects': ['Accounts', 'Leads']}}
            >>> client.new_shim(config)
            {u'id': u'fD9EDV2YROG7pSkBa-hLPg'}

            >>> from squirro_client.exceptions import ClientError
            >>> import pprint
            >>> try:
            ...     client.new_shim({})
            ... except ClientError as ex:
            ...     pprint.pprint(ex.data)
            {u'error': u'invalid shim config',
             u'errors': [u'mandatory squirro attribute "projects" missing',
                         u'mandatory ext attribute "user_id" missing',
                         u'invalid squirro user id "None"']}

        """

        url = '%(endpoint)s/%(version)s/%(tenant)s/shims' % {
            'endpoint': self.bulk_api_url, 'version': self.version,
            'tenant': self.tenant}

        headers = {'Content-Type': 'application/json'}

        res = self._perform_request(
            'post', url, data=json.dumps(config), headers=headers)
        return self._process_response(res, [200, 201])

    def get_user_shims(self, type=None):
        """Returns all known user shims for the provided parameters.

        :param type: Shim type, optional.
        :returns: A list which contains the shims as a dictionary.

        Example::

            >>> client.get_user_shims('my-shim-type')
            [{'id': u'fD9EDV2YROG7pSkBa-hLPg'}]
        """
        url = '%(endpoint)s/%(version)s/%(tenant)s/shims' % {
            'endpoint': self.bulk_api_url, 'version': self.version,
            'tenant': self.tenant}

        headers = {'Content-Type': 'application/json'}
        params = {}
        if type is not None:
            params = {'type': type}

        res = self._perform_request(
            'get', url, params=params, headers=headers)
        return self._process_response(res, [200])

    def new_shim_objects(self, shim_id, job_id, objects, force=False,
                         mode=None):
        """Process new objects for a previously configured shim. Objects
        contain signals which are used to discover provider configurations.

        :param shim_id: Shim identifier.
        :param job_id: Job identifier.
        :param objects: List of objects to be stored.
        :param force: If source discover for objects is to be forced.
        :param mode: Defaults to 'append'
        :returns: A dictionary which contains information about processed
            objects.

        Example::

            >>> client.new_shim_objects('fD9EDV2YROG7pSkBa-hLPg', [])
            {u'delete': 0,
             u'error': 0,
             u'errors': [],
             u'insert': 0,
             u'total': 0,
             u'update': 0}

            >>> objects = [
             {'project': 'Leads',
              'id': '00QE000000EPbFIMA1',
              'name': 'A',
              'signals': {'emails': ['lex@squirro.com'],
                          'firstname': 'John',
                          'lastname': 'Smith',
                          'urls': ['http://squirro.com']},
              'type': 'lead'},
             {'project': 'Accounts',
              'id': '00QE000000APbAPNA7',
              'name': 'Squirro',
              'signals': {'city': u'Z\xfcrich',
                          'company': 'Squirro',
                          'country': 'Switzerland',
                          'emails': [],
                          'urls': ['http://squirro.com']},
              'type': 'account'}]
            >>> client.new_shim_objects('fD9EDV2YROG7pSkBa-hLPg', objects)
            {u'delete': 0,
             u'error': 0,
             u'errors': [],
             u'insert': 2,
             u'total': 2,
             u'update': 0}

            >>> objects = [
             {'project': 'Leads',
              'id': '00QE000000EPbFIMA1',
              'name': 'A',
              'signals': {'emails': ['lex@squirro.com'],
                          'firstname': 'John',
                          'lastname': 'Smith',
                          'urls': ['http://squirro.com']},
              'type': 'lead'},
             {'project': 'Accounts',
              'id': '00QE000000APbAPNA7',
              'name': 'Squirro',
              'signals': {'city': u'Z\xfcrich',
                          'company': 'Squirro',
                          'country': 'Switzerland',
                          'emails': ['info@squirro.com'],
                          'urls': ['http://squirro.com']},
              'type': 'account'}]
            >>> client.new_shim_objects('fD9EDV2YROG7pSkBa-hLPg', objects)
            {u'delete': 0,
             u'error': 0,
             u'errors': [],
             u'insert': 0,
             u'total': 2,
             u'update': 1}

            >>> objects = [
             {'name': 'A', 'signals': {}},
             {'email': 'lex@squirro.com', 'id': '00QE000000EPbFIMA1',
              'signals': {}},
             {'email': 'lex@squirro.com',
              'project': 'Project 1',
              'id': '00QE000000EPbFIMA1',
              'name': 'A',
              'signals': {}}]
            >>> client.new_shim_objects('fD9EDV2YROG7pSkBa-hLPg', objects)
            {u'delete': 0,
             u'error': 3,
             u'errors': [{u'errors': [u'mandatory attribute "id" missing',
                                      u'mandatory attribute "type" missing',
                                      u'mandatory attribute "project" missing',
                                      u'invalid project "None" for object A'],
                          u'index': 0},
                         {u'errors': [u'mandatory attribute "name" missing',
                                      u'mandatory attribute "type" missing',
                                      u'mandatory attribute "project" missing',
                                      u'invalid project "None" for object 0'],
                          u'index': 1},
                         {u'errors': [u'mandatory attribute "type" missing',
                                      u'invalid project "O" for object 0'],
                          u'index': 2}],
             u'insert': 0,
             u'total': 3,
             u'update': 0}

        """

        url = ('%(endpoint)s/%(version)s/%(tenant)s'
               '/shims/%(shim_id)s/objects')
        url = url % {
            'endpoint': self.bulk_api_url, 'version': self.version,
            'tenant': self.tenant, 'shim_id': shim_id}

        headers = {'Content-Type': 'application/json'}
        params = {'job_id': job_id, 'force': force}
        if mode is not None:
            params['mode'] = mode

        res = self._perform_request(
            'post', url, params=params, data=json.dumps(objects),
            headers=headers)
        return self._process_response(res, [200])

    def new_shim_object(self, shim_id, job_id, object_config, force=False):
        """Process the single object configuration for a previously configured
        shim. The single object configuration contains signals which are used
        to discover provider configurations.

        :param shim_id: Shim identifier.
        :param job_id: Job identifier.
        :param object_config: Single object configuration to be stored.
        :param force: If source discovery is to be forced.
        :returns: A dictionary which contains information about the processed
            object.

        Example::

            >>> client.new_shim_object('fD9EDV2YROG7pSkBa-hLPg', {})
            {u'delete': 0,
             u'error': 0,
             u'errors': [],
             u'insert': 0,
             u'total': 0,
             u'update': 0}

            >>> object_config = {
             'project': 'Leads',
              'id': '00QE000000EPbFIMA1',
              'name': 'A',
              'signals': {'emails': ['lex@squirro.com'],
                          'firstname': 'John',
                          'lastname': 'Smith',
                          'urls': ['http://squirro.com']},
              'type': 'lead'}
            >>> client.new_shim_object('fD9EDV2YROG7pSkBa-hLPg', object_config)
            {u'delete': 0,
             u'error': 0,
             u'errors': [],
             u'insert': 1,
             u'total': 1,
             u'update': 0',
             u'object_id': u'zFe3V-3hQlSjPtkIKpjkXg'}
        """

        url = ('%(endpoint)s/%(version)s/%(tenant)s'
               '/shims/%(shim_id)s/object')
        url = url % {
            'endpoint': self.bulk_api_url, 'version': self.version,
            'tenant': self.tenant, 'shim_id': shim_id}

        headers = {'Content-Type': 'application/json'}
        params = {'job_id': job_id, 'force': force}

        res = self._perform_request(
            'post', url, params=params, data=json.dumps(object_config),
            headers=headers)
        return self._process_response(res, [200])

    def get_project_objects(self, project_id, object_ext_ids=None):
        """Get object details for a number of objects from a project.

        :param project_id: Project identifier.
        :param object_ext_ids: List of external object identifiers (optional).
        :returns: A list of dictionaries which contain information about the
            object.

        Example::

            >>> client.get_project_objects(
                'fcBG4gdWRYihW_ZWvQ0dGQ',
                ['00QE000000EPbFIMA1', '00QE000000APbAPNA7'])
            [
                {u'id': u'NyfRri_bTv-QagNS76_AnQ',
                 u'object_id': u'zFe3V-3hQlSjPtkIKpjkXg'},
                {u'id': u'-QMbKG8iR0-l5mYuLgCCQg',
                 u'object_id': u'7emkK1qiQV-BtFeI1qsLLA'},
            ]
        """

        url = ('%(endpoint)s/%(version)s/%(tenant)s/'
               'projects/%(project_id)s/objects')
        url = url % {
            'endpoint': self.bulk_api_url, 'version': self.version,
            'tenant': self.tenant, 'project_id': project_id,
        }

        params = None
        if object_ext_ids is not None:
            params = {'id': object_ext_ids}

        res = self._perform_request('get', url, params=params)
        return self._process_response(res)

    def get_shim_objects(self, shim_id, object_ext_ids=None):
        """Get object details for a number of objects.

        :param shim_id: Shim identifier.
        :param object_ext_ids: List of external object identifiers (optional).
        :returns: A list of dictionaries which contain information about the
            object.

        Example::

            >>> client.get_shim_objects(
                'fD9EDV2YROG7pSkBa-hLPg',
                ['00QE000000EPbFIMA1', '00QE000000APbAPNA7'])
            [
                {u'id': u'NyfRri_bTv-QagNS76_AnQ',
                 u'object_id': u'zFe3V-3hQlSjPtkIKpjkXg'},
                {u'id': u'-QMbKG8iR0-l5mYuLgCCQg',
                 u'object_id': u'7emkK1qiQV-BtFeI1qsLLA'},
            ]
        """

        url = '%(endpoint)s/%(version)s/%(tenant)s/shims/%(shim_id)s/objects'
        url = url % {
            'endpoint': self.bulk_api_url, 'version': self.version,
            'tenant': self.tenant, 'shim_id': shim_id,
        }

        params = None
        if object_ext_ids is not None:
            params = {'id': object_ext_ids}

        res = self._perform_request('get', url, params=params)
        return self._process_response(res)

    def get_shim_object(self, shim_id, object_ext_id):
        """Get object details.

        :param shim_id: Shim identifier.
        :param object_ext_id: External object identifier.
        :returns: A dictionary which contains information about the object.

        Example::

            >>> client.get_shim_object('fD9EDV2YROG7pSkBa-hLPg',
            ...                        '00QE000000EPbFIMA1')
            {u'id': u'NyfRri_bTv-QagNS76_AnQ',
             u'object_id': u'zFe3V-3hQlSjPtkIKpjkXg'}
        """

        url = ('%(endpoint)s/%(version)s/%(tenant)s'
               '/shims/%(shim_id)s/object/%(object_ext_id)s')
        url = url % {
            'endpoint': self.bulk_api_url, 'version': self.version,
            'tenant': self.tenant, 'shim_id': shim_id,
            'object_ext_id': object_ext_id}

        res = self._perform_request('get', url)
        return self._process_response(res)

    def get_bulk_object_signals(self, object_id, keys=None):
        """Returns all known signals which belong to the provided object
        identifier.

        :param object_id: Topic identifier.
        :param keys: List of signal keys.
        :returns: A dictionary which contains the object signals.

        Example::

            >>> c.get_object_signals('o1-9lew6SmCG9GcfskZ8vQ')
            {u'emails': u'["info@atlassian.com"]',
             u'urls': u'["http://www.atlassian.com/"]'}
        """

        url = '%(endpoint)s/%(version)s/%(tenant)s/signals/%(object_id)s' % {
            'endpoint': self.bulk_api_url, 'version': self.version,
            'tenant': self.tenant, 'object_id': object_id}

        # build params
        params = {}
        if keys is not None:
            params['keys'] = ','.join(keys)

        res = self._perform_request('get', url, params=params)
        return self._process_response(res)

    def new_shim_job(self, shim_id):
        """Create a new job for the provided shim identifier.

        :param shim_id: Shim identifier.
        :returns: A dictionary which contains the job identifier to be used for
            future operations.

        Example::

            >>> client.new_shim_job('fD9EDV2YROG7pSkBa-hLPg')
            {u'audit_log': [[u'2013-05-16T12:06:08',
                             u'triangle3.local',
                             u'H5Qv-WhgSBGW0WL8xolSCQ',
                             u'xXV-rTxDQQmdqMxxUWSZpQ',
                             u'created job REQ9WyLqQ8KNkuhkh6N04w']],
             u'created_at': u'2013-05-16T12:06:08',
             u'id': u'REQ9WyLqQ8KNkuhkh6N04w',
             u'modified_at': u'2013-05-16T12:06:08',
             u'shim_id': u'xXV-rTxDQQmdqMxxUWSZpQ',
             u'status': u'unknown'}
        """
        url = ('%(endpoint)s/%(version)s/%(tenant)s'
               '/shims/%(shim_id)s/jobs')
        url = url % {
            'endpoint': self.bulk_api_url, 'version': self.version,
            'tenant': self.tenant, 'shim_id': shim_id}

        res = self._perform_request('post', url)
        return self._process_response(res, [201])

    def get_shim_job(self, shim_id, job_id):
        """Get job details.

        :param shim_id: Shim identifier.
        :param job_id: Job identifier.
        :returns: A dictionary which contains information about the job.

        Example::

            >>> client.get_shim_job('fD9EDV2YROG7pSkBa-hLPg',
            ...                     '0_NkfaKeRzWCX5XIIUdjfg')
            {u'audit_log': [[u'2013-05-16T12:06:08',
                             u'triangle3.local',
                             u'H5Qv-WhgSBGW0WL8xolSCQ',
                             u'xXV-rTxDQQmdqMxxUWSZpQ',
                             u'created job REQ9WyLqQ8KNkuhkh6N04w']],
             u'created_at': u'2013-05-16T12:06:08',
             u'id': u'REQ9WyLqQ8KNkuhkh6N04w',
             u'modified_at': u'2013-05-16T12:06:08',
             u'shim_id': u'xXV-rTxDQQmdqMxxUWSZpQ',
             u'status': u'unknown'}
        """

        url = ('%(endpoint)s/%(version)s/%(tenant)s'
               '/shims/%(shim_id)s/jobs/%(job_id)s')
        url = url % {
            'endpoint': self.bulk_api_url, 'version': self.version,
            'tenant': self.tenant, 'shim_id': shim_id, 'job_id': job_id}

        res = self._perform_request('get', url)
        return self._process_response(res, [200])

    def update_shim_job(self, shim_id, job_id, data):
        """Update job details.

        :param shim_id: Shim identifier.
        :param job_id: Job identifier.
        :param data: A dictionary which can contain the following keys:
            * `status`: New status of the job.
            * `msg`: A status message.

        Example::

            >>> data = {'status': 'completed', 'msg': 'all done'}
            >>> client.update_shim_job('D9EDV2YROG7pSkBa-hLPg',
            ...                        '0_NkfaKeRzWCX5XIIUdjfg', data)
            >>> client.get_shim_job('fD9EDV2YROG7pSkBa-hLPg',
            ...                     '0_NkfaKeRzWCX5XIIUdjfg')
            {u'audit_log': [[u'2013-05-16T12:06:08',
                             u'triangle3.local',
                             u'H5Qv-WhgSBGW0WL8xolSCQ',
                             u'xXV-rTxDQQmdqMxxUWSZpQ',
                             u'created job REQ9WyLqQ8KNkuhkh6N04w'],
                            [u'2013-05-16T12:09:25',
                             u'triangle3.local',
                             u'H5Qv-WhgSBGW0WL8xolSCQ',
                             u'xXV-rTxDQQmdqMxxUWSZpQ',
                             u'all done'],
                            [u'2013-05-16T12:09:25',
                             u'triangle3.local',
                             u'H5Qv-WhgSBGW0WL8xolSCQ',
                             u'xXV-rTxDQQmdqMxxUWSZpQ',
                             u'update status to completed']],
             u'created_at': u'2013-05-16T12:06:08',
             u'id': u'REQ9WyLqQ8KNkuhkh6N04w',
             u'modified_at': u'2013-05-16T12:09:25',
             u'shim_id': u'xXV-rTxDQQmdqMxxUWSZpQ',
             u'status': u'completed'}
        """

        url = ('%(endpoint)s/%(version)s/%(tenant)s'
               '/shims/%(shim_id)s/jobs/%(job_id)s')
        url = url % {
            'endpoint': self.bulk_api_url, 'version': self.version,
            'tenant': self.tenant, 'shim_id': shim_id, 'job_id': job_id}

        headers = {'Content-Type': 'application/json'}

        res = self._perform_request(
            'put', url, data=json.dumps(data), headers=headers)
        return self._process_response(res, [204])

    def new_shim_items(self, shim_id, job_id, source_id, source_secret, items):
        """Process new items for a previously configured shim. The items are
        to be stored in the source identified by the provided source
        identifier and corresponding secret.

        :param shim_id: Shim identifier.
        :param source_id: Source identifier.
        :param source_secret: Source secret.
        :param job_id: Job identifier.
        :param items: List of items to be uploaded.
        :returns: A dictionary which contains information about processed
            items.

        Example::

            >>> items = [{'id': 'item01', 'title': 'my title'}]
            >>> client.new_shim_items('fD9EDV2YROG7pSkBa-hLPg', 'source01',
            ...                       'secret01', items)
            {u'duplicate': 0,
             u'error': 0,
             u'errors': [],
             u'job_id': 'default',
             u'queued': 0,
             u'total': 0}
        """

        url = ('%(endpoint)s/%(version)s/%(tenant)s'
               '/shims/%(shim_id)s/source/%(source_id)s/%(source_secret)s')
        url = url % {
            'endpoint': self.bulk_api_url, 'version': self.version,
            'tenant': self.tenant, 'shim_id': shim_id,
            'source_id': source_id, 'source_secret': source_secret}

        headers = {'Content-Type': 'application/json'}
        params = {'job_id': job_id}

        res = self._perform_request(
            'post', url, params=params, data=json.dumps(items),
            headers=headers)
        return self._process_response(res, [200])
