# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for 
# license information.
# ------------------------------------------------------------------------------

# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t; python-indent: 4 -*-

"""
    MLServer    
"""


from __future__ import absolute_import

# python 2 and python 3 compatibility library
from six import iteritems
from ..models import CreateSnapshotResponse


class SnapshotsApi(object):
    """
    SnapshotApi
    """

    def __init__(self, http_client):
        self._http_client = http_client
   
    def create_snapshot(self, id, create_snapshot_request, **kwargs):
        """
        Create Snapshot
        Create a snapshot from session by saving the workspace and all files in 
        the working directory into zip file, the return value will be the 
        created snapshot Id.
                
        :param str id: Id of the session. (required)
        :param CreateSnapshotRequest create_snapshot_request: Properties of the 
        new snapshot. (required)
        :return: CreateSnapshotResponse                 
        """

        all_params = ['id', 'create_snapshot_request']
        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method create_snapshot" % key
                )
            params[key] = val
        
        del params['kwargs']

        # verify the required parameter 'id' is set
        if ('id' not in params) or (params['id'] is None):
            raise ValueError("Missing the required parameter `id` when calling `create_snapshot`")
        
        # verify the required parameter 'create_snapshot_request' is set
        if ('create_snapshot_request' not in params) or (params['create_snapshot_request'] is None):
            raise ValueError("Missing the required parameter `create_snapshot_request` when calling `create_snapshot`")
            
        resource = '/sessions/' + id + '/snapshot'
        body = create_snapshot_request.to_dict()        
        response = self._http_client.post(resource, json=body).json()
        return CreateSnapshotResponse(snapshot_id = response.get('snapshotId'))
   
    def delete_snapshot(self, id, **kwargs):
        """
        Delete Snapshot
        Delete a snapshot permanently and also it's content (zip file containing 
        the working directory files and the workspace file)

        :param str id: Id of the snapshot. (required)
        :return: str                 
        """

        all_params = ['id']
        
        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_snapshot" % key
                )
            params[key] = val
        
        del params['kwargs']

        # verify the required parameter 'id' is set
        if ('id' not in params) or (params['id'] is None):
            raise ValueError("Missing the required parameter `id` when calling `delete_snapshot`")
        
        return self._http_client.delete('/snapshots/' + id)