# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from collections import OrderedDict
from ._util import TraversalFunction

model_show_header_to_fn_dict = OrderedDict([('Name', TraversalFunction(('Name',))),
                                            ('Id', TraversalFunction(('Id',))),
                                            ('Version', TraversalFunction(('Version',))),
                                            ('Created_At', TraversalFunction(('CreatedAt',))),
                                            ('Tags', TraversalFunction(('Tags',))),
                                            ('Description', TraversalFunction(('Description',))),
                                            ('Url', TraversalFunction(('Url',)))])
