import json


class ProjectsMixin(object):

    PROJECT_ATTRIBUTES = set([
        'default_search', 'title', 'default_sort', 'locator',
    ])

    def get_user_projects(self, owner_id=None, include_objects=False):
        """Get projects for the provided user.

        :param owner_id: User identifier which owns the projects.
        :param include_objects: Whether to include object information, either
            `True` or `False`.
        :returns: A list of projects.

        Example::

            >>> client.get_user_projects()
            [{u'id': u'Sz7LLLbyTzy_SddblwIxaA',
              u'title': u'My Contacts',
              u'objects': 1,
              u'type': u'my contacts'},
             {u'id': u'2aEVClLRRA-vCCIvnuEAvQ',
              u'title': u'My Organizations',
              u'objects': 2,
              u'type': u'my organizations'}]

        """

        url = '%(ep)s/%(version)s/%(tenant)s/projects' % {
            'ep': self.topic_api_url, 'version': self.version,
            'tenant': self.tenant
        }

        # build params
        params = {'include_objects': include_objects}
        if owner_id is not None:
            params['owner_id'] = owner_id

        res = self._perform_request('get', url, params=params)
        return self._process_response(res)

    def get_project(self, project_id):
        """Get project details.

        :param project_id: Project identifier.
        :returns: A dictionary which contains the project.

        Example::

            >>> client.get_project('2aEVClLRRA-vCCIvnuEAvQ')
            {u'id': u'2aEVClLRRA-vCCIvnuEAvQ',
             u'title': u'My Organizations',
             u'type': u'my organizations'}

        """

        url = '%(ep)s/%(version)s/%(tenant)s/projects/%(project_id)s' % {
            'ep': self.topic_api_url, 'version': self.version,
            'tenant': self.tenant, 'project_id': project_id}

        res = self._perform_request('get', url)
        return self._process_response(res)

    def new_project(self, title, owner_id=None, locator=None,
                    default_sort=None):
        """Create a new project.

        :param title: Project title.
        :param owner_id: User identifier which owns the objects.
        :param locator: Custom index locator configuration which is a
            dictionary which contains the `index_server` (full URI including
            the port for index server) key.
            For advanced usage the locator can also be split into a reader and
            a writer locator: {"reader": {"index_server":
            "https://reader:9200"}, "writer": {"index_server":
            "https://writer:9200"}}
        :param default_sort: Custom default sort configuration which is a
            dictionary which contains the `sort` (valid values are `date` and
            `relevance`) and `order` (valid values are `asc` and `desc`) keys.
        :returns: A dictionary which contains the project identifier.

        Example::

            >>> locator = {'index_server': 'http://10.0.0.1:9200'}
            >>> default_sort = [{'relevance': {'order': 'asc'}}]
            >>> client.new_project('My Project', locator=locator,
            ...                    default_sort=default_sort)
            {u'id': u'gd9eIipOQ-KobU0SwJ8VcQ'}
        """

        url = '%(ep)s/%(version)s/%(tenant)s/projects' % {
            'ep': self.topic_api_url, 'version': self.version,
            'tenant': self.tenant}

        # build data
        data = {'title': title}
        if owner_id is not None:
            data['owner_id'] = owner_id
        if locator is not None:
            data['locator'] = json.dumps(locator)
        if default_sort is not None:
            data['default_sort'] = json.dumps(default_sort)

        res = self._perform_request('post', url, data=data)
        return self._process_response(res, [201])

    def modify_project(self, project_id, **kwargs):
        """Modify a project.

        :param project_id: Project identifier.
        :param kwargs: Query parameters. All keyword arguments are passed on
            verbatim to the API. See the
            [[Projects#Update Project|Update Project]] resource for all
            possible parameters.

        Example::

            >>> client.modify_project('gd9eIipOQ-KobU0SwJ8VcQ',
            ...                       title='My Other Project')

        """
        url = '%(ep)s/%(version)s/%(tenant)s/projects/%(project_id)s' % {
            'ep': self.topic_api_url, 'version': self.version,
            'tenant': self.tenant, 'project_id': project_id}

        # build data
        data = {}
        for key in self.PROJECT_ATTRIBUTES:
            if key in kwargs:
                data[key] = kwargs[key]

        headers = {'Content-Type': 'application/json'}

        res = self._perform_request(
            'put', url, data=json.dumps(data), headers=headers)
        return self._process_response(res, [201, 204])

    def delete_project(self, project_id):
        """Delete a project.

        :param project_id: Project identifier.

        Example::

            >>> client.delete_project('gd9eIipOQ-KobU0SwJ8VcQ')

        """

        url = '%(ep)s/%(version)s/%(tenant)s/projects/%(project_id)s' % {
            'ep': self.topic_api_url, 'version': self.version,
            'tenant': self.tenant, 'project_id': project_id}

        res = self._perform_request('delete', url)
        self._process_response(res, [204])

    def reset_project(self, project_id, reset_dashboards=None,
                      reset_elasticsearch_index=None, reset_facets=None):
        """Resets different entities of a project based on boolean flags.

        :param project_id: Project identifier.
        :param reset_dashboards: Boolean flag to decide whether to reset the
            project dashboards or not. If True, will delete all the dashboards
            in the current project. Defaults to False if not specified.
        :param reset_elasticsearch_index: Boolean flag to decide whether to
            reset/delete all documents in a project's elasticsearch index or
            not without deleting the index itself. Defaults to False if not
            specified.
        :param reset_facets: Boolean flag to decide whether to delete all the
            facets in the project. This needs the `reset_elasticsearch_index`
            flag to be set to True. Be aware that all the dashboards and other
            Squirro entities dependent on the current facets will stop working
            with the reset of facets.
            Defaults to False if not specified.

        Example::

            >>> client.reset_project(
                    'gd9eIipOQ-KobU0SwJ8VcQ', reset_dashboards=True,
                    reset_elasticsearch_index=True, reset_facets=True)

        """

        url = '%(ep)s/%(version)s/%(tenant)s/projects/%(project_id)s/reset' % {
            'ep': self.topic_api_url, 'version': self.version,
            'tenant': self.tenant, 'project_id': project_id}

        headers = {'Content-Type': 'application/json'}

        args = {
            'reset_dashboards': reset_dashboards,
            'reset_elasticsearch_index': reset_elasticsearch_index,
            'reset_facets': reset_facets
        }
        data = dict([(k, v) for k, v in args.iteritems() if v is not None])

        if data:
            res = self._perform_request(
                'post', url, data=json.dumps(data), headers=headers)
        else:
            res = {}
        self._process_response(res, [200])
