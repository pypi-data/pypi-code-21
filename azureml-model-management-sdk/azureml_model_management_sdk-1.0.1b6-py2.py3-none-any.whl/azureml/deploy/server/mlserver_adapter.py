# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for 
# license information.
# ------------------------------------------------------------------------------

# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t; python-indent: 4 -*-

"""
Overview
========

Contains an implementation of an HTTP adapter for requests that automatically
create `mls` URLs and other custom `mls` settings on a request.
"""
from requests.adapters import HTTPAdapter


class MLServerAdapter(HTTPAdapter):
    """
    A MLServer Transport Adapter for HTTP Requests.    
    """

    def __init__(self,  **kwargs):
        # Pass through. We can do custom mls things here
        super(MLServerAdapter, self).__init__(**kwargs)        

    def send(self, request, **kwargs):
        """
        Sends a PreparedRequest object.
        :param request: The Requests :class:`PreparedRequest <PreparedRequest>` 
        object to send.
        """

        # Pass through. We can do custom mls things here
        return super(MLServerAdapter, self).send(request, **kwargs)

    def build_response(self, request, response):
        """
        Builds a Response object from a urllib3 response. 
        :param request: The Requests :class:`PreparedRequest <PreparedRequest>`          
        :param response: The urllib3 response.
        """

        # Pass through. We can do custom mls things here
        resp = super(MLServerAdapter, self).build_response(request, response)
        return resp        
