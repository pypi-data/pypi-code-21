# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from collections import OrderedDict
from ._util import TraversalFunction


image_show_header_to_fn_dict = OrderedDict([('Name', TraversalFunction(('Name',))),
                                            ('Version', TraversalFunction(('Version',))),
                                            ('Id', TraversalFunction(('Id',))),
                                            ('Description', TraversalFunction(('Description',))),
                                            ('Image_Type', TraversalFunction(('ImageType',))),
                                            ('Manifest_Id', TraversalFunction(('Manifest','Id')))])
