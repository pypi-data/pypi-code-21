# ****************       BEGIN-STANDARD-COPYRIGHT      ***************
#
# Copyright (c) 2017, Spirent Communications.
#
# All rights reserved. Proprietary and confidential information of Spirent Communications.
#
#  ***************        END-STANDARD-COPYRIGHT       ***************

class UriIdentity(object):
    """ Base class for any resources in SLC with URI identity """
    def __init__(self, uri):
        """Initialize a URI identity object"""
        self._uri = uri

    @property
    def uri(self):
        """ Return a topology URI"""
        return self._uri
