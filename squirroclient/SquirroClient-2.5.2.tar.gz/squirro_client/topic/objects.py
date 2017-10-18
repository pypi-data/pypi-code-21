import json


class ObjectsMixin(object):

    TOPIC_ATTRIBUTES = set([
        'title', 'is_ready', 'query', 'type', 'owner_id',
    ])

    def get_user_objects(self, project_id, full=None, start=None, count=None,
                         api_version='v0'):
        """Get all objects for the provided user.

        :param project_id: Project identifier from which the objects should be
            returned.
        :param full: If set to `True`, then include subscription and source
            details in the response.
        :param start: Integer. Used for pagination of objects. If set, the
            objects starting with offset `start` are returned. Defaults to 0.
        :param count: Integer. Used for pagination of objects. If set, `count`
            objects are returned. Defaults to 100.
        :param api_version: API version to use. Pagination (`start` and `count`
            needs API version `v1`).
        :returns: A list which contains the objects.

        Example::

            >>> client.get_user_objects(project_id='Sz7LLLbyTzy_SddblwIxaA',
                                        api_version='v1')
            {u'count': 100,
             u'start': 0,
             u'next_params': {u'count': 100, u'start': 100}
             u'objects':[{u'project_id': u'Sz7LLLbyTzy_SddblwIxaA',
              u'id': u'zFe3V-3hQlSjPtkIKpjkXg',
              u'is_ready': True,
              u'needs_preview': False,
              u'noise_level': None,
              u'title': u'A',
              u'type': u'contact'}]}
        """
        if api_version == 'v0' and (start is not None or count is not None):
            raise NotImplementedError(
                'For pagination support use API version v1')

        url = ('%(ep)s/%(version)s/%(tenant)s'
               '/projects/%(project_id)s/objects')
        url = url % {
            'ep': self.topic_api_url, 'version': api_version,
            'tenant': self.tenant, 'project_id': project_id}
        if full:
            url += '/full'

        args = {
            'start': start,
            'count': count,
        }
        args = dict([(k, v) for k, v in args.iteritems() if v is not None])

        res = self._perform_request('get', url, params=args)
        return self._process_response(res)

    def get_object(self, project_id, object_id):
        """Get object details.

        :param project_id: Project identifier.
        :param object_id: Object identifier.
        :returns: A dictionary which contains the object.

        Example::

            >>> client.get_object('2aEVClLRRA-vCCIvnuEAvQ',
            ...                   '2sic33jZTi-ifflvQAVcfw')
            {u'project_id': u'2aEVClLRRA-vCCIvnuEAvQ',
             u'id': u'2sic33jZTi-ifflvQAVcfw',
             u'is_ready': True,
             u'managed_subscription': False,
             u'needs_preview': False,
             u'noise_level': None,
             u'subscriptions': [u'3qTRv4W9RvuOxcGwnnAYbg',
                                u'hw8j7LUBRM28-jAellgQdA',
                                u'4qBkea4bTv-QagNS76_akA',
                                u'NyfRri_2SUa_JNptx0JAnQ',
                                u'oTvI6rlaRmKvmYCfCvLwpw',
                                u'c3aEwdz5TMefc_u7hCl4PA',
                                u'Xc0MN_7KTAuDOUbO4mhG6A',
                                u'y1Ur-vLuRmmzUNMi4xGrJw',
                                u'iTdms4wgTRapn1ehMqJgwA',
                                u'MawimNPKSlmpeS9YlMzzaw'],
             u'subscriptions_processed': True,
             u'title': u'Squirro',
             u'type': u'organization'}

        """

        url = ('%(ep)s/%(version)s/%(tenant)s'
               '/projects/%(project_id)s/objects/%(object_id)s') % {
                   'ep': self.topic_api_url, 'version': self.version,
                   'tenant': self.tenant, 'project_id': project_id,
                   'object_id': object_id
               }

        res = self._perform_request('get', url)
        return self._process_response(res)

    def new_object(self, project_id, title, owner_id=None, type=None,
                   is_ready=None):
        """Create a new object.

        :param project_id: Project identifier.
        :param title: Object title.
        :param owner_id: User identifier which owns the objects.
        :param type: Object type.
        :param is_ready: Object `is_ready` flag, either `True` or `False`.
        :returns: A dictionary which contains the project identifier and the
            new object identifier.

        Example::

            >>> client.new_object(
            ...     'H5Qv-WhgSBGW0WL8xolSCQ', '2aEVClLRRA-vCCIvnuEAvQ',
            ...     'Memonic', type='organization')
            {u'project_id': u'2aEVClLRRA-vCCIvnuEAvQ',
             u'id': u'2TBYtWgRRIa23h1rEveI3g'}

        """

        url = ('%(ep)s/%(version)s/%(tenant)s/projects/%(project_id)s/'
               'objects') % {
                   'ep': self.topic_api_url, 'version': self.version,
                   'tenant': self.tenant, 'project_id': project_id
               }

        # build data
        data = {'title': title}
        user_values = locals()
        for key in self.TOPIC_ATTRIBUTES:
            if user_values.get(key) is not None:
                data[key] = user_values[key]

        res = self._perform_request('post', url, data=data)
        return self._process_response(res, [201])

    def modify_object(self, project_id, object_id, title=None,
                      is_ready=None, noise_level=None):
        """Modify an object.

        :param project_id: Project identifier for the object.
        :param object_id: Object identifier.
        :param title: New object title.
        :param is_ready: New object `is_ready` flag, either `True` for `False`.
        :param noise_level: New object noise level. Can be any float value from
            0.0 to 1.0.
        :returns: A dictionary which contains the object.

        Example::

            >>> client.modify_object('2aEVClLRRA-vCCIvnuEAvQ',
            ...                      '2TBYtWgRRIa23h1rEveI3g', is_ready=False)
            {}

        """

        url = ('%(ep)s/%(version)s/%(tenant)s'
               '/projects/%(project_id)s/objects/%(object_id)s') % {
                   'ep': self.topic_api_url, 'version': self.version,
                   'tenant': self.tenant, 'project_id': project_id,
                   'object_id': object_id
               }

        # build data
        data = {}
        user_values = locals()
        for key in self.TOPIC_ATTRIBUTES:
            if user_values.get(key) is not None:
                data[key] = user_values[key]

        headers = {'Content-Type': 'application/json'}

        res = self._perform_request(
            'put', url, data=json.dumps(data), headers=headers)
        return self._process_response(res, [201, 204])

    def delete_object(self, project_id, object_id):
        """Delete a object.

        :param project_id: Project identifier.
        :param object_id: Object identifier.

        Example::

            >>> client.delete_object('2aEVClLRRA-vCCIvnuEAvQ',
            ...                      '2TBYtWgRRIa23h1rEveI3g')

        """

        url = ('%(ep)s/%(version)s/%(tenant)s'
               '/projects/%(project_id)s/objects/%(object_id)s') % {
                   'ep': self.topic_api_url, 'version': self.version,
                   'tenant': self.tenant, 'project_id': project_id,
                   'object_id': object_id
               }

        res = self._perform_request('delete', url)
        self._process_response(res, [204])

    def pause_object(self, project_id, object_id, subscription_ids=None):
        """Pause all (or some) subscriptions of an object.

        :param project_id: Project identifier.
        :param object_id: Object identifier.
        :param subscription_ids: Optional, list of subscription identifiers.
            Only pause these subscriptions of the object.

        Example::

            >>> client.pause_object('2aEVClLRRA-vCCIvnuEAvQ',
            ...                     '2TBYtWgRRIa23h1rEveI3g')

        """

        url = ('%(ep)s/%(version)s/%(tenant)s'
               '/projects/%(project_id)s/objects/%(object_id)s/pause') % {
                   'ep': self.topic_api_url, 'version': self.version,
                   'tenant': self.tenant, 'project_id': project_id,
                   'object_id': object_id
               }

        data = {}
        if subscription_ids:
            data = {'subscription_ids': subscription_ids}

        headers = {'Content-Type': 'application/json'}

        res = self._perform_request('post', url, data=json.dumps(data),
                                    headers=headers)
        self._process_response(res, [200, 204])

    def resume_object(self, project_id, object_id, subscription_ids=None):
        """Resume all (or some) paused subscriptions of an object.

        :param project_id: Project identifier.
        :param object_id: Object identifier.
        :param subscription_ids: Optional, list of subscription identifiers.
            Only resume these subscriptions of the object.

        Example::

            >>> client.resume_object('2aEVClLRRA-vCCIvnuEAvQ',
            ...                      '2TBYtWgRRIa23h1rEveI3g')

        """

        url = ('%(ep)s/%(version)s/%(tenant)s'
               '/projects/%(project_id)s/objects/%(object_id)s/resume') % {
                   'ep': self.topic_api_url, 'version': self.version,
                   'tenant': self.tenant, 'project_id': project_id,
                   'object_id': object_id
               }

        data = {}
        if subscription_ids:
            data = {'subscription_ids': subscription_ids}

        headers = {'Content-Type': 'application/json'}

        res = self._perform_request('post', url, data=json.dumps(data),
                                    headers=headers)
        self._process_response(res, [200, 204])

    #
    # Object Signals
    #

    def get_object_signals(self, project_id, object_id, flat=False):
        """Return a dictionary of object signals for a object.

        :param project_id: Project identifier.
        :param object_id: Object identifier.
        :param flat: Set to `True` to receive a simpler dictionary
            representation. The `seeder` information is not displayed in that
            case.
        :returns: Dictionary of signals on this object.

        Example::

            >>> client.get_object_signals(
            ...     'gd9eIipOQ-KobU0SwJ8VcQ', '2sic33jZTi-ifflvQAVcfw')
            {'signals': [{u'key': u'email_domain',
                          u'value': 'nestle.com',
                          u'seeder': 'salesforce'}]}

            >>> client.get_object_signals(
            ...     'gd9eIipOQ-KobU0SwJ8VcQ', '2sic33jZTi-ifflvQAVcfw',
            ...     flat=True)
            {u'email_domain': 'nestle.com'}
        """
        url = ('%(ep)s/%(version)s/%(tenant)s'
               '/projects/%(project_id)s/objects/%(object_id)s/signals')
        url = url % {
            'ep': self.topic_api_url, 'version': self.version,
            'tenant': self.tenant, 'project_id': project_id,
            'object_id': object_id}

        res = self._perform_request('get', url)
        retval = self._convert_flat(flat, self._process_response(res, [200]))
        return retval

    def update_object_signals(self, project_id, object_id, signals,
                              seeder=None, flat=False):
        """Updates the object signals of a object.

        :param project_id: Project identifier.
        :param object_id: Object identifier.
        :param signals: List of all objects to update. Only signals that exist
            in this list will be touched, the others are left intact. Use the
            value `None` for a key to delete that signal.
        :param seeder: Seeder that owns these signals. Should be set for
            automatically written values.
        :param flat: Set to `True` to pass in and receive a simpler dictionary
            representation. The `seeder` information is not displayed in that
            case.
        :returns: List or dictionary of all signals of that object in the same
            format as returned by `get_object_signals`.

        Example::

            >>> client.update_object_signals(
            ...     'gd9eIipOQ-KobU0SwJ8VcQ', '2sic33jZTi-ifflvQAVcfw',
            ...     [{'key': 'essentials', 'value': [
            ...       'discovery-baseobject-A96PWkLzTIWSJy3WMsvzzw']}])
            [
                {u'key': u'essentials',
                 u'value': [u'discovery-baseobject-A96PWkLzTIWSJy3WMsvzzw'],
                 u'seeder': None},
                {u'key': u'email_domain',
                 u'value': 'nestle.com',
                 u'seeder': 'salesforce'}
            ]

            >>> client.update_object_signals(
            ...     'gd9eIipOQ-KobU0SwJ8VcQ', '2sic33jZTi-ifflvQAVcfw',
            ...     {'essentials': [
            ...         'discovery-baseobject-A96PWkLzTIWSJy3WMsvzzw']},
            ...     flat=True)
            {u'essentials': [u'discovery-baseobject-A96PWkLzTIWSJy3WMsvzzw'],
             u'email_domain': u'nestle.com'}
        """
        url = ('%(ep)s/%(version)s/%(tenant)s'
               '/projects/%(project_id)s/objects/%(object_id)s/signals')
        url = url % {
            'ep': self.topic_api_url, 'version': self.version,
            'tenant': self.tenant, 'project_id': project_id,
            'object_id': object_id}

        if flat:
            signals = [{'key': key, 'value': value}
                       for key, value in signals.iteritems()]

        data = {'signals': signals, 'seeder': seeder}

        headers = {'Content-Type': 'application/json'}
        res = self._perform_request(
            'post', url, data=json.dumps(data), headers=headers)
        retval = self._convert_flat(flat, self._process_response(res, [200]))
        return retval

    def _convert_flat(self, flat, retval):
        """Converts the object API response to the flat format.
        """
        if flat:
            retval = dict([(s['key'], s['value']) for s in retval['signals']])
        return retval
