from .baseclient import BaseClient, iter_not_none


class ProjectClient(BaseClient):
    def add_project_tags(self, project, tags):
        """add tags to a project

        Example:
            >>> client.add_project_tags("8a21a1af-6e1e-51d6-9c3f-fc40561d3da2", ['some', 'example', 'tags']).data
            {
                "owner": "riskiq",
                "description": "",
                "active": true,
                "guid": "8a21a1af-6e1e-51d6-9c3f-fc40561d3da2",
                "tags": [
                    "example",
                    "some",
                    "tags"
                ],
                "created": "2017-07-11T19:19:01.023000",
                "creator": "john.smith@riskiq.net",
                "collaborators": [],
                "success": true,
                "can_edit": true,
                "subscribers": [
                    "john.smith@riskiq.net",
                    "john.smith@riskiq.net"
                "visibility": "public",
                "links": {
                    "tag": "/v2/project/tag?project=8a21a1af-6e1e-51d6-9c3f-fc40561d3da2",
                    "artifact": "/v2/artifact?project=8a21a1af-6e1e-51d6-9c3f-fc40561d3da2",
                    "self": "/v2/project?project=8a21a1af-6e1e-51d6-9c3f-fc40561d3da2"
                },
                "organization": "riskiq",
                "name": "example project",
                "featured": false
            }

        Args:
            project (str): Project GUID
            tags (list): Project tags to add

        Returns:
            dict: new project tags
        """
        data = dict(iter_not_none(
            project=project, tags=tags
        ))
        return self.post('/project/tag', data=data)

    def remove_project_tags(self, project, tags):
        """remove tags from a project

        Example:

            >>> client.remove_project_tags("8a21a1af-6e1e-51d6-9c3f-fc40561d3da2", ['some']).data
            {
                "owner": "riskiq",
                "description": "",
                "active": true,
                "guid": "8a21a1af-6e1e-51d6-9c3f-fc40561d3da2",
                "tags": [
                    "example",
                    "tags"
                ],
                "created": "2017-07-11T19:19:01.023000",
                "creator": "john.smith@riskiq.net",
                "collaborators": [],
                "success": true,
                "can_edit": true,
                "subscribers": [
                    "john.smith@riskiq.net",
                    "john.smith@riskiq.net"
                ],
                "visibility": "public",
                "links": {
                    "tag": "/v2/project/tag?project=8a21a1af-6e1e-51d6-9c3f-fc40561d3da2",
                    "artifact": "/v2/artifact?project=8a21a1af-6e1e-51d6-9c3f-fc40561d3da2",
                    "self": "/v2/project?project=8a21a1af-6e1e-51d6-9c3f-fc40561d3da2"
                },
                "organization": "riskiq",
                "name": "example project",
                "featured": false
            }

        Args:
            project (str): Project GUID
            tags (list): Project tags to remove

        Returns:
            dict: new project tags
        """
        data = dict(iter_not_none(
            project=project, tags=tags
        ))
        return self.delete('/project/tag', data=data)

    def set_project_tags(self, project, tags):
        """set tags for a project

        Example:

            >>> client.set_project_tags("8a21a1af-6e1e-51d6-9c3f-fc40561d3da2", ['new', 'example', 'tags']).data
            {
                "creator": "john.smith@riskiq.net",
                "tags": [
                    "example",
                    "new",
                    "tags"
                ],
                "owner": "riskiq",
                "description": "",
                "can_edit": true,
                "links": {
                    "artifact": "/v2/artifact?project=8a21a1af-6e1e-51d6-9c3f-fc40561d3da2",
                    "tag": "/v2/project/tag?project=8a21a1af-6e1e-51d6-9c3f-fc40561d3da2",
                    "self": "/v2/project?project=8a21a1af-6e1e-51d6-9c3f-fc40561d3da2"
                },
                "collaborators": [],
                "name": "new example",
                "subscribers": [
                    "yonathan@riskiq.net",
                    "john.smith@riskiq.net"
                ],
                "guid": "8a21a1af-6e1e-51d6-9c3f-fc40561d3da2",
                "active": true,
                "featured": false,
                "visibility": "private",
                "success": true,
                "created": "2017-07-11T19:19:01.023000",
                "organization": "riskiq"
            }

        Args:
            project (str): Project GUID
            tags (list): new project tags

        Returns:
            dict: new project tags
        """
        data = dict(iter_not_none(
            project=project, tags=tags
        ))
        return self.put('/project/tag', data=data)

    def get_project(self, project=None, owner=None, creator=None,
                    organization=None, visibility=None, featured=None):
        """find a project using a search filter

        Example:

            >>> client.get_project("8a21a1af-6e1e-51d6-9c3f-fc40561d3da2").data
            {
                "creator": "john.smith@riskiq.net",
                "tags": [
                    "example",
                    "some",
                    "tags"
                ],
                "owner": "riskiq",
                "description": "",
                "can_edit": true,
                "links": {
                    "artifact": "/v2/artifact?project=8a21a1af-6e1e-51d6-9c3f-fc40561d3da2",
                    "tag": "/v2/project/tag?project=8a21a1af-6e1e-51d6-9c3f-fc40561d3da2",
                    "self": "/v2/project?project=8a21a1af-6e1e-51d6-9c3f-fc40561d3da2"
                },
                "collaborators": [],
                "name": "example project",
                "subscribers": [
                    "john.smith@riskiq.net",
                    "john.smith@riskiq.net"
                "guid": "8a21a1af-6e1e-51d6-9c3f-fc40561d3da2",
                "active": true,
                "featured": false,
                "visibility": "public",
                "success": true,
                "created": "2017-07-11T19:19:01.023000",
                "organization": "riskiq"
            }

        Args:
            project (str): Project GUID
            owner (str, optional): username of the user who owns the project
            creator (str, optional): username of the user who created the
                project
            organization (str, optional): name of the organization that owns
                the project
            visibility (str, optional): visibility, ``public`` or ``private``
            featured (bool, optional): featured status

        Returns:
            dict: matching projects
        """
        data = dict(iter_not_none(
            project=project, owner=owner, creator=creator,
            organization=organization, visibility=visibility,
            featured=featured
        ))
        if 'featured' in data and not isinstance(data['featured'], bool):
            raise ValueError('featured must be a bool')
        if 'visibility' in data and data['visibility'] not in ('public',
                                                               'private'):
            raise ValueError('visibility must be public or private')
        return self.get('/project', data=data)

    def update_project(self, project, name=None, description=None,
                       visibility=None, featured=None, tags=None):
        """update a project using a GUID

        Example:

            >>> client.update_project("8a21a1af-6e1e-51d6-9c3f-fc40561d3da2", name='new example', tags=['tags'], visibility='private').data
            {
                "owner": "riskiq",
                "description": "",
                "active": true,
                "guid": "8a21a1af-6e1e-51d6-9c3f-fc40561d3da2",
                "tags": [
                    "tags"
                ],
                "created": "2017-07-11T19:19:01.023000",
                "creator": "john.smith@riskiq.net",
                "collaborators": [],
                "success": true,
                "can_edit": true,
                "subscribers": [
                    "john.smith@riskiq.net",
                    "john.smith@riskiq.net"
                ],
                "visibility": "private",
                "links": {
                    "tag": "/v2/project/tag?project=8a21a1af-6e1e-51d6-9c3f-fc40561d3da2",
                    "artifact": "/v2/artifact?project=8a21a1af-6e1e-51d6-9c3f-fc40561d3da2",
                    "self": "/v2/project?project=8a21a1af-6e1e-51d6-9c3f-fc40561d3da2"
                },
                "organization": "riskiq",
                "name": "new example",
                "featured": false
            }

        Note:
            use :func:`add_project_tags` or :func:`remove_project_tags` to
            update tags without setting them

        Args:
            project (str): Project GUID
            name (str, optional): new name for the project
            description (str, optional): new description for the project
            visibility (str, optional): visibility, ``public`` or ``private``
            featured (bool, optional): featured status
            tags (list, optional): new tags for the project

        Returns:
            dict: project with new settings
        """
        if not project:
            raise ValueError('project must be a UUID string')
        project = str(project)
        data = dict(iter_not_none(
            project=project, name=name, description=description,
            visibility=visibility, featured=featured, tags=tags
        ))
        if 'featured' in data and not isinstance(data['featured'], bool):
            raise ValueError('featured must be a bool')
        if 'visibility' in data and data['visibility'] not in ('public',
                                                               'private'):
            raise ValueError('visibility must be public or private')
        return self.post('/project', data=data)

    def create_project(self, name, visibility='public', description=None,
                       featured=False, tags=None):
        """create a new project

        Example:

            >>> client.create_project("example project").data
            {
                "featured": false,
                "links": {
                    "self": "/v2/project?project=8a21a1af-6e1e-51d6-9c3f-fc40561d3da2",
                    "tag": "/v2/project/tag?project=8a21a1af-6e1e-51d6-9c3f-fc40561d3da2",
                    "artifact": "/v2/artifact?project=8a21a1af-6e1e-51d6-9c3f-fc40561d3da2"
                },
                "created": "2017-07-11T19:19:01.023796",
                "visibility": "public",
                "organization": "riskiq",
                "description": "",
                "collaborators": [],
                "can_edit": true,
                "active": true,
                "success": true,
                "tags": [],
                "creator": "john.smith@riskiq.net",
                "subscribers": [
                    "john.smith@riskiq.net",
                    "john.smith@riskiq.net"
                ],
                "owner": "riskiq",
                "guid": "8a21a1af-6e1e-51d6-9c3f-fc40561d3da2",
                "name": "example project"
            }

        Args:
            name (str): name for the project
            description (str, optional): description for the project
            visibility (str, optional): visibility, ``public`` or ``private``
                defaults to ``public``
            featured (bool, optional): featured status, defaults to ``False``
            tags (list, optional): tags for the project

        Returns:
            dict: newly created project
        """
        data = dict(iter_not_none(
            name=name, visibility=visibility, tags=tags,
            description=description, featured=featured,
        ))
        if 'featured' in data and not isinstance(data['featured'], bool):
            raise ValueError('featured must be a bool')
        if 'visibility' in data and data['visibility'] not in ('public',
                                                               'private'):
            raise ValueError('visibility must be public or private')
        return self.put('/project', data=data)

    def delete_project(self, project):
        """delete a project

        Example:

            >>> client.delete_project("8a21a1af-6e1e-51d6-9c3f-fc40561d3da2").data
            {
                "creator": "john.smith@riskiq.net",
                "tags": [
                    "example",
                    "new",
                    "tags"
                ],
                "owner": "riskiq",
                "description": "",
                "can_edit": true,
                "links": {
                    "artifact": "/v2/artifact?project=8a21a1af-6e1e-51d6-9c3f-fc40561d3da2",
                    "tag": "/v2/project/tag?project=8a21a1af-6e1e-51d6-9c3f-fc40561d3da2",
                    "self": "/v2/project?project=8a21a1af-6e1e-51d6-9c3f-fc40561d3da2"
                },
                "collaborators": [],
                "name": "new example",
                "subscribers": [
                    "john.smith@riskiq.net",
                    "john.smith@riskiq.net",
                    "john.smith@riskiq.net",
                ],
                "guid": "8a21a1af-6e1e-51d6-9c3f-fc40561d3da2",
                "active": true,
                "featured": false,
                "visibility": "private",
                "success": true,
                "created": "2017-07-11T19:19:01.023000",
                "organization": "riskiq"
            }

        Args:
            project (str): Project GUID

        Returns:
            dict: deleted project
        """
        if not project:
            raise ValueError('project must be a UUID string')
        project = str(project)
        return self.delete('/project', data={'project': project})
