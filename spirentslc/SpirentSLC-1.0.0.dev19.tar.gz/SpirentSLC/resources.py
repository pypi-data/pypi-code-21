# ****************       BEGIN-STANDARD-COPYRIGHT      ***************
#
# Copyright (c) 2017, Spirent Communications.
#
# All rights reserved. Proprietary and confidential information of Spirent Communications.
#
#  ***************        END-STANDARD-COPYRIGHT       ***************

"""Parameter file class and necessary tools."""

from .identity import UriIdentity

class ParameterFile(UriIdentity):
    """Parameter file representation.
    """
    def __init__(self, uri):
        """Initiates a new topology.

        Arguments:
        uri -- parameter file URI, e.g. project://my_project/parameter_files/parameters.ffpt
        """

        UriIdentity.__init__(self, uri)

    def __str__(self):
        """ Return a URI """
        return self._uri

class ResponseMapFile(UriIdentity):
    """Responsemap file representation.
    """
    def __init__(self, uri):
        """Initiates a new topology.

        Arguments:
        uri -- parameter file URI, e.g. project://my_project/response_maps/my_map.ffrm
        """
        UriIdentity.__init__(self, uri)

    def __str__(self):
        """ Return a URI """
        return self._uri
