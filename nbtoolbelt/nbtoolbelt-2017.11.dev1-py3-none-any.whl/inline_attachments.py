"""
NbConvert Preprocessor to inline attachments

Copyright (c) 2017 - Eindhoven University of Technology, The Netherlands

This software is made available under the terms of the MIT License.

Parts of this code are reworked from the rendernb checklet for Momotor <momotor.org>.
"""

from nbconvert.preprocessors import Preprocessor
from nbformat import NotebookNode
from typing import Any, Dict, Tuple
import base64
from urllib.parse import quote


class InlineAttachmentsPreprocessor(Preprocessor):
    """To embed cell attachments inside the cell's source.
    """

    ACCEPTABLE_TYPES = (
        'image/png',
        'image/jpeg',
        'image/gif',
        'image/webp',
        'image/bmp',
    )

    def preprocess_cell(self, cell: NotebookNode, resources: Dict[str, Any], index: int) -> \
            Tuple[NotebookNode, Dict[str, Any]]:
        """Take a Jupyter Notebook cell and inline all attachments as data.

        .. note:: **Modifies**: ``cell``

        :param cell: cell for which to inline attachments
        :param resources: global resources
        :param index: cell index in notebook
        :return: modified cell, updated resources
        """
        if 'attachments' in cell:
            remaining_attachments = {}

            for name, data in cell.attachments.items():
                data_type, data_content = None, None
                # data_content = next((data[data_type] for data_type in data if data_type in ACCEPTABLE_TYPES), None)
                for data_type in data:
                    if data_type in self.ACCEPTABLE_TYPES:
                        data_content = data[data_type]
                        break

                if data_content:
                    # Re-encode base64 to strip whitespace
                    try:
                        decoded_content = base64.b64decode(data_content)
                    except TypeError:
                        pass
                    else:
                        recoded_content = base64.b64encode(decoded_content)

                    old_uri = 'attachment:' + quote(name)
                    new_uri = 'data:{};base64,{}'.format(quote(data_type), quote(recoded_content))

                    cell.source = cell.source.replace(old_uri, new_uri)

                else:
                    remaining_attachments[name] = data

            cell['attachments'] = remaining_attachments

        return cell, resources
