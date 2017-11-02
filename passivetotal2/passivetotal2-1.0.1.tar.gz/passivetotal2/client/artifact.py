from .baseclient import BaseClient, iter_not_none


class ArtifactClient(BaseClient):
    def get_artifact(self, artifact=None, creator=None, organization=None,
                     owner=None, project=None, query=None, artifact_type=None):
        """Gets an artifact that matches the params

        at least one param should be specified, if none are, the command is
        likely to time out.

        Example:

            >>> client.get_artifact(query="example.com").data
            {
                "artifacts": [
                    {
                        "user_tags": [
                            "example"
                        ],
                        "monitor": False,
                        "creator": "john.smith@riskiq.net",
                        "tags": [
                            "example",
                            "registered"
                        ],
                        "owner": "riskiq",
                        "guid": "2f6a1373-dece-59f6-709a-cbacfc366bf9",
                        "project": "8a21a1af-6e1e-51d6-9c3f-fc40561d3da2",
                        "monitorable": True,
                        "links": {
                            "tag": "/v2/artifact/tag?artifact=2f6a1373-dece-59f6-709a-cbacfc366bf9",
                            "self": "/v2/artifact?artifact=2f6a1373-dece-59f6-709a-cbacfc366bf9",
                            "project": "/v2/project?project=8a21a1af-6e1e-51d6-9c3f-fc40561d3da2"
                        },
                        "type": "domain",
                        "system_tags": [
                            "registered"
                        ],
                        "tag_meta": {
                            "example": {
                                "created_at": "2017-07-11T19:46:53.969000",
                                "creator": "john.smith@riskiq.net"
                            }
                        },
                        "organization": "riskiq",
                        "created": "2017-07-11T19:46:53.927000",
                        "query": "example.com"
                    }
                ],
                "success": True
            }


        Args:
            artifact (str, optional): UUID of the Artifact
            creator (str, optional): creator of the artifact
            organization (str, optional): org that owns the artifact
            owner (str, optional): user that owns the artifact
            project (str, optional): project that contains the artifact
            query (str, optional): query used to create the artifact
            artifact_type (str, optional): type of the artifact

        Returns:
            dict: all artifacts that match the search
        """
        data = dict(iter_not_none(
            artifact=artifact, creator=creator, organization=organization,
            owner=owner, project=project, query=query, type=artifact_type
        ))
        return self.get('/artifact', data=data)

    def update_artifact(self, artifact, monitor=None, tags=None):
        """updates an artifact

        Example:

            >>> client.update_artifact("c2be40d4-ccd8-eaec-95a9-eee386afe544", monitor=False).data
            {
                "user_tags": [
                    "example"
                ],
                "monitor": true,
                "creator": "john.smith@riskiq.net",
                "owner": "riskiq",
                "guid": "c2be40d4-ccd8-eaec-95a9-eee386afe544",
                "project": "8a21a1af-6e1e-51d6-9c3f-fc40561d3da2",
                "monitorable": true,
                "links": {
                    "tag": "/v2/artifact/tag?artifact=c2be40d4-ccd8-eaec-95a9-eee386afe544",
                    "self": "/v2/artifact?artifact=c2be40d4-ccd8-eaec-95a9-eee386afe544",
                    "project": "/v2/project?project=8a21a1af-6e1e-51d6-9c3f-fc40561d3da2"
                },
                "type": "domain",
                "system_tags": [
                    "registered"
                ],
                "tag_meta": {
                    "example": {
                        "created_at": "2017-07-11T19:53:10.870000",
                        "creator": "john.smith@riskiq.net"
                    }
                },
                "organization": "riskiq",
                "success": {
                    "monitor": true,
                    "tags": true
                },
                "created": "2017-07-11T19:53:10.848000",
                "query": "example2.com"
            }


        Note:
            if you want to update tags without setting everything at once, use
            :func:`add_artifact_tags` or :func:`delete_artifact_tags`

        Note:
            if you want to update multiple artifacts at once, use
            :func:`update_artifact_bulk` or :func:`update_artifacts`

        Args:
            artifact (str): UUID of the Artifact
            tags (list, optional): new list of tags for the artifact
            monitor (bool, optional): whether or not the artifact should be monitored

        Returns:
            dict: updated artifact
        """
        data = dict(iter_not_none(
            artifact=artifact, monitor=monitor, tags=tags,
        ))
        return self.post('/artifact', data=data)

    def create_artifact(self, query, project=None, artifact_type=None,
                        tags=None):
        """creates a new artifact

        Example:
            >>> client.create_artifact("example.com", project="8a21a1af-6e1e-51d6-9c3f-fc40561d3da2", artifact_type='domain', tags=['example']).data
            {
                "user_tags": [
                    "example"
                ],
                "monitor": false,
                "creator": "john.smith@riskiq.net",
                "owner": "riskiq",
                "guid": "2f6a1373-dece-59f6-709a-cbacfc366bf9",
                "project": "8a21a1af-6e1e-51d6-9c3f-fc40561d3da2",
                "monitorable": true,
                "links": {
                    "tag": "/v2/artifact/tag?artifact=2f6a1373-dece-59f6-709a-cbacfc366bf9",
                    "self": "/v2/artifact?artifact=2f6a1373-dece-59f6-709a-cbacfc366bf9",
                    "project": "/v2/project?project=8a21a1af-6e1e-51d6-9c3f-fc40561d3da2"
                },
                "type": "domain",
                "system_tags": [
                    "registered"
                ],
                "tag_meta": {
                    "example": {
                        "created_at": "2017-07-11T19:46:53.969000",
                        "creator": "john.smith@riskiq.net"
                    }
                },
                "organization": "riskiq",
                "success": true,
                "created": "2017-07-11T19:46:53.927000",
                "query": "example.com"
            }

        Args:
            query (str): query to make the artifact
            project (str): project to add the artifact to
            type (str, optional): the type of the artifact, inferred if
                not specified
            tags (list, optional): list of tags for the artifact

        Returns:
            dict: new artifact
        """
        if not project:
            raise ValueError('requires project guid to create artifact')
        data = dict(iter_not_none(
            query=query, project=project, type=artifact_type, tags=tags,
        ))
        return self.put('/artifact', data=data)

    def delete_artifact(self, artifact):
        """deletes an artifact

        Example:
            >>> client.delete_artifact("c2be40d4-ccd8-eaec-95a9-eee386afe544").data
            {
                "query": "example2.com",
                "system_tags": [
                    "registered"
                ],
                "project": "8a21a1af-6e1e-51d6-9c3f-fc40561d3da2",
                "organization": "riskiq",
                "monitor": true,
                "links": {
                    "self": "/v2/artifact?artifact=c2be40d4-ccd8-eaec-95a9-eee386afe544",
                    "tag": "/v2/artifact/tag?artifact=c2be40d4-ccd8-eaec-95a9-eee386afe544",
                    "project": "/v2/project?project=8a21a1af-6e1e-51d6-9c3f-fc40561d3da2"
                },
                "tag_meta": {
                    "example": {
                        "created_at": "2017-07-11T19:53:10.870000",
                        "creator": "john.smith@riskiq.net"
                    }
                },
                "created": "2017-07-11T19:53:10.848000",
                "creator": "john.smith@riskiq.net",
                "user_tags": [
                    "example"
                ],
                "success": true,
                "owner": "riskiq",
                "guid": "c2be40d4-ccd8-eaec-95a9-eee386afe544",
                "monitorable": true,
                "type": "domain"
            }

        if you want to update multiple artifacts at once, use
        :func:`delete_artifacts`

        Args:
            artifact (str): UUID of the artifact

        Returns:
            dict: the artifact you just deleted
        """
        return self.delete('/artifact', data={'artifact': artifact})

    def get_artifact_tags(self, artifact):
        """gets tags for an artifact

        Example:

            >>> client.get_artifact_tags("2f6a1373-dece-59f6-709a-cbacfc366bf9").data
            {
                "success": true,
                "user_tags": [
                    "example"
                ],
                "system_tags": [
                    "registered"
                ],
                "tag_meta": {
                    "example": {
                        "created_at": "2017-07-11T19:46:53.969000",
                        "creator": "john.smith@riskiq.net"
                    }
                }
            }


        Args:
            artifact (str): UUID of the artifact

        Returns:
            dict: the tags of the artifact
        """
        return self.get('/artifact/tag', data={'artifact': artifact})

    def add_artifact_tags(self, artifact, tags):
        """adds tags to an artifact

        Example:
            >>> client.add_artifact_tags("2f6a1373-dece-59f6-709a-cbacfc366bf9", ['tags']).data
            {
                "tag_meta": {
                    "example": {
                        "created_at": "2017-07-11T19:46:53.969000",
                        "creator": "john.smith@riskiq.net"
                    },
                    "tags": {
                        "created_at": "2017-07-11T19:50:44.265000",
                        "creator": "john.smith@riskiq.net"
                    }
                },
                "user_tags": [
                    "example",
                    "tags"
                ],
                "system_tags": [
                    "registered"
                ],
                "success": true
            }

        Args:
            artifact (str): UUID of the artifact
            tags (list): list of tags you want added to the artifact

        Returns:
            dict: the new tags of the artifact
        """
        tags = tags or []
        return self.post('/artifact/tag', data={'artifact': artifact,
                                                'tags': tags})

    def set_artifact_tags(self, artifact, tags):
        """sets tags for an artifact

        Example:
            >>> client.set_artifact_tags("2f6a1373-dece-59f6-709a-cbacfc366bf9",
                                         ['example', 'tags']).data
            {
                "tag_meta": {
                    "example": {
                        "created_at": "2017-07-11T19:51:51.229000",
                        "creator": "john.smith@riskiq.net"
                    },
                    "tags": {
                        "created_at": "2017-07-11T19:51:53.697000",
                        "creator": "john.smith@riskiq.net"
                    }
                },
                "user_tags": [
                    "example",
                    "tags"
                ],
                "system_tags": [
                    "registered"
                ],
                "success": true
            }


        Args:
            artifact (str): UUID of the artifact
            tags (list): list of tags you want the artifact to have

        Returns:
            dict: the new tags of the artifact
        """
        tags = tags or []
        return self.put('/artifact/tag', data={'artifact': artifact,
                                               'tags': tags})

    def delete_artifact_tags(self, artifact, tags):
        """deletes tags from an artifact

        Example:

            >>> client.delete_artifact_tags("2f6a1373-dece-59f6-709a-cbacfc366bf9", ['tags']).data
            {
                "success": true,
                "user_tags": [
                    "example"
                ],
                "system_tags": [
                    "registered"
                ],
                "tag_meta": {
                    "example": {
                        "created_at": "2017-07-11T19:46:53.969000",
                        "creator": "john.smith@riskiq.net"
                    }
                }
            }

        Args:
            artifact (str): UUID of the artifact
            tags (list): list of tags you want to delete from the artifact

        Returns:
            dict: the new tags of the artifact
        """
        tags = tags or []
        return self.delete('/artifact/tag', data={'artifact': artifact,
                                                  'tags': tags})

    def update_artifact_bulk(self, artifacts):
        """Bulk update for artifacts

        Args:
            artifacts (list): a list of dictionaries that represent
                artifacts to update
                ::
                    [
                        {
                            "artifact": "00000000-0000-0000-0000-000000000000",
                            "monitor": True,
                            "tags": []
                        },
                        {
                            "artifact": "00000000-0000-0000-0000-000000000000",
                            "monitor": False,
                            "tags": ["RIG"]
                        }
                    ]


        Returns:
            dict: newly updated artifacts
        """
        data = []
        for artifact_data in artifacts:
            data.append(dict(iter_not_none(artifact_data)))
        return self.post('/artifact/bulk', data={'artifacts': data})

    def create_artifact_bulk(self, artifacts):
        """Bulk create artifacts

        Args:
            artifacts (list): a list of dictionaries that represent
                artifacts to create
                ::
                    [
                        {
                            "query": "passivetotal.org",
                            "type": "domain",
                            "project": example_project,
                            "tags": ["passivetotal", "riskiq"]
                        },
                        {
                            "artifact": "riskiq.net",
                            "type": "domain",
                            "project": example_project,
                            "tags": ["riskiq"]
                        }
                    ]

        Returns:
            dict: newly created artifacts
        """
        data = []
        for artifact_data in artifacts:
            data.append(dict(iter_not_none(artifact_data)))
        return self.put('/artifact/bulk', data={'artifacts': data})

    def delete_artifacts(self, artifact_guids):
        """Bulk delete artifacts

        Args:
            artifact_guids (list): a list of artifact guids

        Returns:
            dict: deleted artifacts
        """
        return self.delete('/artifact/bulk', data={'artifacts': artifact_guids})

    def create_artifacts(self, queries, project=None, artifact_type=None,
                         tags=None):
        """Bulk create artifacts

        functions like :func:`create_artifact_bulk`, except the same settings
        are applied to all newly created artifacts

        Args:
            queries (list): a list of queries for artifacts
            artifact_type (str): the type of all newly created artifacts
            tags (list): tags to apply to all newly created artifacts

        Returns:
            dict: newly created artifacts
        """
        data = [
            dict(iter_not_none(
                query=query, type=artifact_type, project=project, tags=tags,
            ))
            for query in queries
        ]
        return self.put('/artifact/bulk', data={'artifacts': data})

    def update_artifacts(self, artifact_guids, monitor=None, tags=None):
        """Bulk update artifacts

        functions like :func:`update_artifact_bulk`, except the same update
        is applied to all artifacts

        Example:
            >>> client.update_artifacts(["c2be40d4-ccd8-eaec-95a9-eee386afe544", "2f6a1373-dece-59f6-709a-cbacfc366bf9"], monitor=True).data
            {
                "2f6a1373-dece-59f6-709a-cbacfc366bf9": {
                    "owner": "riskiq",
                    "monitor": true,
                    "guid": "2f6a1373-dece-59f6-709a-cbacfc366bf9",
                    "tag_meta": {
                        "tags": {
                            "created_at": "2017-07-11T19:51:53.697000",
                            "creator": "john.smith@riskiq.net"
                        },
                        "example": {
                            "created_at": "2017-07-11T19:51:51.229000",
                            "creator": "john.smith@riskiq.net"
                        }
                    },
                    "user_tags": [
                        "example",
                        "tags"
                    ],
                    "creator": "john.smith@riskiq.net",
                    "system_tags": [
                        "registered"
                    ],
                    "monitorable": true,
                    "success": {
                        "tags": true,
                        "monitor": true
                    },
                    "type": "domain",
                    "links": {
                        "project": "/v2/project?project=8a21a1af-6e1e-51d6-9c3f-fc40561d3da2",
                        "tag": "/v2/artifact/tag?artifact=2f6a1373-dece-59f6-709a-cbacfc366bf9",
                        "self": "/v2/artifact?artifact=2f6a1373-dece-59f6-709a-cbacfc366bf9"
                    },
                    "query": "example.com",
                    "organization": "riskiq",
                    "project": "8a21a1af-6e1e-51d6-9c3f-fc40561d3da2",
                    "created": "2017-07-11T19:46:53.927000"
                },
                "c2be40d4-ccd8-eaec-95a9-eee386afe544": {
                    "owner": "riskiq",
                    "monitor": true,
                    "guid": "c2be40d4-ccd8-eaec-95a9-eee386afe544",
                    "tag_meta": {
                        "example": {
                            "created_at": "2017-07-11T19:53:10.870000",
                            "creator": "john.smith@riskiq.net"
                        }
                    },
                    "user_tags": [
                        "example"
                    ],
                    "creator": "john.smith@riskiq.net",
                    "system_tags": [
                        "registered"
                    ],
                    "monitorable": true,
                    "success": {
                        "tags": true,
                        "monitor": true
                    },
                    "type": "domain",
                    "links": {
                        "project": "/v2/project?project=8a21a1af-6e1e-51d6-9c3f-fc40561d3da2",
                        "tag": "/v2/artifact/tag?artifact=c2be40d4-ccd8-eaec-95a9-eee386afe544",
                        "self": "/v2/artifact?artifact=c2be40d4-ccd8-eaec-95a9-eee386afe544"
                    },
                    "query": "example2.com",
                    "organization": "riskiq",
                    "project": "8a21a1af-6e1e-51d6-9c3f-fc40561d3da2",
                    "created": "2017-07-11T19:53:10.848000"
                }
            }


        Args:
            artifact_guids (list): a list of artifact guids
            monitor (str): the new monitor status for all listed artifacts
            tags (list): tags to apply to all listed artifacts

        Returns:
            dict: updated artifacts
        """
        data = [
            dict(iter_not_none(
                artifact=guid, monitor=monitor, tags=tags,
            ))
            for guid in artifact_guids
        ]
        return self.post('/artifact/bulk', data={'artifacts': data})
