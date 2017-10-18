import json


class SubscriptionsMixin(object):

    def get_object_subscriptions(self, project_id, object_id, user_id=None,
                                 filter_deleted=None):
        """Get all subscriptions for the provided object.

        :param project_id: Project identifier.
        :param object_id: Object identifier.
        :param user_id: User identifier.
        :param filter_deleted: If `True` returns only non-deleted
            subscriptions.
        :returns: A list which contains subscriptions.

        Example::

            >>> client.get_object_subscriptions('2sic33jZTi-ifflvQAVcfw',
            ...                                 '2TBYtWgRRIa23h1rEveI3g')
            [
                {
                    u'config': {
                        u'market': u'de-CH',
                        u'query': u'squirro',
                        u'vertical': u'News',
                    },
                    u'deleted': False,
                    u'id': u'hw8j7LUBRM28-jAellgQdA',
                    u'link': u'http://bing.com/news/search?q=squirro',
                    u'modified_at': u'2012-10-09T07:54:12',
                    u'provider': u'bing',
                    u'seeder': None,
                    u'source_id': u'2VkLodDHTmiMO3rlWi2MVQ',
                    u'title': u'News Alerts for "squirro" in Switzerland',
                }
            ]
        """

        url = ('%(ep)s/%(version)s/%(tenant)s'
               '/projects/%(project_id)s'
               '/objects/%(object_id)s/subscriptions')
        url = url % {
            'ep': self.topic_api_url, 'version': self.version,
            'tenant': self.tenant, 'project_id': project_id,
            'object_id': object_id}

        # build params
        params = {}
        if user_id is not None:
            params['user_id'] = user_id
        if filter_deleted is not None:
            params['filter_deleted'] = filter_deleted

        res = self._perform_request('get', url, params=params)
        return self._process_response(res)

    def get_subscription(self, project_id, object_id, subscription_id):
        """Get subscription details.

        :param project_id: Project identifier.
        :param object_id: Object identifier.
        :param subscription_id: Subscription identifier.
        :returns: A dictionary which contains the subscription.

        Example::

            >>> client.get_subscription(
            ...     '2sic33jZTi-ifflvQAVcfw', '2TBYtWgRRIa23h1rEveI3g',
            ...     'hw8j7LUBRM28-jAellgQdA')
            {
                u'config': {
                    u'market': u'de-CH',
                    u'query': u'squirro',
                    u'vertical': u'News',
                },
                u'deleted': False,
                u'id': u'hw8j7LUBRM28-jAellgQdA',
                u'link': u'http://bing.com/news/search?q=squirro',
                u'modified_at': u'2012-10-09T07:54:12',
                u'provider': u'bing',
                u'seeder': None,
                u'source_id': u'2VkLodDHTmiMO3rlWi2MVQ',
                u'title': u'News Alerts for "squirro" in Switzerland',
                u'processed': True,
                u'paused': False,
            }
        """

        url = ('%(ep)s/%(version)s/%(tenant)s'
               '/projects/%(project_id)s'
               '/objects/%(object_id)s/subscriptions/%(subscription_id)s')
        url = url % {
            'ep': self.topic_api_url, 'version': self.version,
            'tenant': self.tenant, 'project_id': project_id,
            'object_id': object_id,
            'subscription_id': subscription_id}

        res = self._perform_request('get', url)
        return self._process_response(res)

    def new_subscription(self, project_id, object_id, provider, config,
                         user_id=None, seeder=None, private=None):
        """Create a new subscription.

        :param project_id: Project identifier.
        :param object_id: Object identifier.
        :param provider: Provider name.
        :param config: Provider configuration dictionary.
        :param user_id: User identifier.
        :param seeder: Seeder which manages the subscription.
        :param private: Hints that the contents for this subscriptions should
            be treated as private.
        :returns: A dictionary which contains the new subscription.

        Example::

            >>> client.new_subscription(
            ...     '2sic33jZTi-ifflvQAVcfw', '2TBYtWgRRIa23h1rEveI3g',
            ...     'feed', {'url': 'http://blog.squirro.com/rss'})
            {u'config': {u'url': u'http://blog.squirro.com/rss'},
             u'deleted': False,
             u'id': u'oTvI6rlaRmKvmYCfCvLwpw',
             u'link': u'http://blog.squirro.com/rss',
             u'modified_at': u'2012-10-12T09:32:09',
             u'provider': u'feed',
             u'seeder': u'team',
             u'source_id': u'D3Q8AiPoTg69bIkqFhe3Bw',
             u'title': u'Squirro',
             u'processed': False,
             u'paused': False}

        """

        url = ('%(ep)s/%(version)s/%(tenant)s'
               '/projects/%(project_id)s'
               '/objects/%(object_id)s/subscriptions')
        url = url % {
            'ep': self.topic_api_url, 'version': self.version,
            'tenant': self.tenant, 'project_id': project_id,
            'object_id': object_id}

        # inject token for dataloader provider
        if provider == 'dataloader':
            dataloader_options = config.get('dataloader_options', {})
            dataloader_options['token'] = self.refresh_token
            config['dataloader_options'] = dataloader_options

        # build data
        data = {
            'provider': provider, 'config': json.dumps(config)
        }
        if user_id is not None:
            data['user_id'] = user_id
        if seeder is not None:
            data['seeder'] = seeder
        if private is not None:
            data['private'] = private

        res = self._perform_request('post', url, data=data)
        return self._process_response(res, [200, 201])

    def modify_subscription(self, project_id, object_id, subscription_id,
                            config=None):
        """Modify an existing subscription.

        :param project_id: Project identifier.
        :param object_id: Object identifier.
        :param subscription_id: Subscription identifier.
        :param config: Changed config of the subscription.

        Example::

            >>> client.modify_subscription(
            ...     '2sic33jZTi-ifflvQAVcfw',
            ...     '2TBYtWgRRIa23h1rEveI3g',
            ...     'oTvI6rlaRmKvmYCfCvLwpw',
            ...     config={'url': 'http://blog.squirro.com/atom'})
        """

        url = ('%(ep)s/%(version)s/%(tenant)s'
               '/projects/%(project_id)s'
               '/objects/%(object_id)s/subscriptions/%(subscription_id)s')
        url = url % {
            'ep': self.topic_api_url, 'version': self.version,
            'tenant': self.tenant, 'project_id': project_id,
            'object_id': object_id, 'subscription_id': subscription_id}

        # build data
        data = {}
        if config is not None:
            data['config'] = json.dumps(config)

        res = self._perform_request('put', url, data=data)
        return self._process_response(res, [200])

    def delete_subscription(self, project_id, object_id, subscription_id,
                            seeder=None):
        """Delete an existing subscription.

        :param project_id: Project identifier.
        :param object_id: Object identifier.
        :param subscription_id: Subscription identifier.
        :param seeder: Seeder that deletes the subscription.

        Example::

            >>> client.delete_subscription('2sic33jZTi-ifflvQAVcfw',
            ...                            '2TBYtWgRRIa23h1rEveI3g',
            ...                            'oTvI6rlaRmKvmYCfCvLwpw')

        """

        url = ('%(ep)s/%(version)s/%(tenant)s'
               '/projects/%(project_id)s'
               '/objects/%(object_id)s/subscriptions/%(subscription_id)s')
        url = url % {
            'ep': self.topic_api_url, 'version': self.version,
            'tenant': self.tenant, 'project_id': project_id,
            'object_id': object_id,
            'subscription_id': subscription_id}

        # build params
        params = {}
        if seeder is not None:
            params['seeder'] = seeder

        res = self._perform_request('delete', url, params=params)
        self._process_response(res, [204])

    def pause_subscription(self, project_id, object_id, subscription_id):
        """Pause a subscription.

        :param project_id: Project identifier.
        :param object_id: Object identifier.
        :param subscription_id: Subscription identifier.

        Example::

            >>> client.pause_subscription('2sic33jZTi-ifflvQAVcfw',
            ...                           '2TBYtWgRRIa23h1rEveI3g',
            ...                           'hw8j7LUBRM28-jAellgQdA')
        """

        url = ('%(ep)s/%(version)s/%(tenant)s/projects/%(project_id)s'
               '/objects/%(object_id)s/subscriptions/%(subscription_id)s/'
               'pause')
        url = url % {
            'ep': self.topic_api_url, 'version': self.version,
            'tenant': self.tenant, 'project_id': project_id,
            'object_id': object_id,
            'subscription_id': subscription_id}

        res = self._perform_request('post', url)
        self._process_response(res, [200, 204])

    def resume_subscription(self, project_id, object_id, subscription_id):
        """Resume a paused subscription.

        :param project_id: Project identifier.
        :param object_id: Object identifier.
        :param subscription_id: Subscription identifier.

        Example::

            >>> client.resume_subscription(
            ...     '2sic33jZTi-ifflvQAVcfw', '2TBYtWgRRIa23h1rEveI3g',
            ...     'hw8j7LUBRM28-jAellgQdA')
        """

        url = ('%(ep)s/%(version)s/%(tenant)s'
               '/projects/%(project_id)s'
               '/objects/%(object_id)s/subscriptions/%(subscription_id)s/'
               'resume')
        url = url % {
            'ep': self.topic_api_url, 'version': self.version,
            'tenant': self.tenant, 'project_id': project_id,
            'object_id': object_id,
            'subscription_id': subscription_id}

        res = self._perform_request('post', url)
        self._process_response(res, [200, 204])
