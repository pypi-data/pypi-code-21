# -*- coding: utf-8 -*-
"""
Datary sdk Modify Operations File
"""
import os
import re
import json

from urllib.parse import urljoin
from datary.datasets import DataryDatasets
from datary.operations.limits import DataryOperationLimits
from scrapbag import (add_element, force_list, get_element, get_dimension,
                      remove_list_duplicates, flatten, dict2orderedlist,
                      exclude_empty_values)
import structlog

logger = structlog.getLogger(__name__)


class DataryModifyOperation(DataryDatasets, DataryOperationLimits):
    """
    Datary ModifyOperation module class
    """

    _ROWZEROHEADER_CONFIDENCE_VALUE = 0.5

    def modify_request(self, wdir_uuid, element, **kwargs):
        """
        Make Modify requests
        ============   =======   ==============================================
        Parameter      Type      Description
        ============   =======   ==============================================
        wdir_uuid      str       working directory uuid
        element        dict      element (dict) with Datary model data fields.
        ============   ======   ===============================================
        """
        url = urljoin(self.URL_BASE,
                      "workdirs/{}/changes".format(wdir_uuid))
        headers = kwargs.get('headers', self.headers)
        payload = {
            "action": "modify",
            "filemode": 100644,
            "dirname": element.get('path'),
            "basename": element.get('basename'),
            "kern": json.dumps(element.get('data', {}).get('kern')),
            "meta": json.dumps(element.get('data', {}).get('meta'))}

        response = self.request(
            url, 'POST', **{'data': payload, 'headers': headers})

        if response:
            logger.info(
                "File has been modified in workdir.",
                url=url,
                # payload=payload,
                dirname=element.get('path'),
                basename=element.get('basename'),
                # element=element
                )

    def modify_file(self, wdir_uuid, element, mod_style='override', **kwargs):
        """
        Modifies an existing file in Datary.

        ===============   ===============   ==================================
        Parameter         Type              Description
        ===============   ===============   ==================================
        wdir_uuid         str               working directory uuid
        element           list              [path, basename, data, sha1]
        mod_style         str o callable    'override' by default,
                                            'update-append' mod_style,
                                            'update-row' mod_style,
                                            <callable> function to use.
        ===============   ===============   ==================================
        """
        # Override method
        if mod_style == 'override':
            self.override_file(wdir_uuid, element, **kwargs)

        # Update Append method
        elif mod_style == 'update-append':
            self.update_append_file(wdir_uuid, element, **kwargs)

        # TODO: ADD update-row method

        # Inject own modify solution method
        elif callable(mod_style):
            mod_style(wdir_uuid, element, callback_request=self.modify_request)

        # Default..
        else:
            logger.error('NOT VALID modify style passed.')

    def override_file(self, wdir_uuid, element, **kwargs):
        """
        Override an existing file in Datary.

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        wdir_uuid         str             working directory uuid
        element           list            [path, basename, data, sha1]
        ================  =============   ====================================
        """
        logger.info("Override an existing file in Datary.")

        self.modify_request(wdir_uuid, element, **kwargs)

    def update_append_file(self, wdir_uuid, element, repo_uuid, **kwargs):
        """
        Update append an existing file in Datary.

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        wdir_uuid         str             working directory uuid
        element           list            [path, basename, data, sha1]
        ================  =============   ====================================

        """
        logger.info("Update an existing file in Datary.")
        try:

            # retrieve original dataset_uuid from datary
            stored_dataset_uuid = self.get_dataset_uuid(
                wdir_uuid=wdir_uuid,
                path=element.get('path', ''),
                basename=element.get('basename', ''))

            # retrieve original dataset from datary
            stored_element = self.get_original(
                dataset_uuid=stored_dataset_uuid,
                repo_uuid=repo_uuid,
                wdir_uuid=wdir_uuid)

            if not stored_element:
                msg = ('Fail to retrieve original data ({}) from Datary'
                       ' workdir({}):( ')
                raise Exception(msg.format(stored_dataset_uuid, wdir_uuid))

            # update elements
            self.update_elements(stored_element, element)

            # introduce stored_element into element data
            element['data'] = {
                'kern': stored_element.get('__kern'),
                'meta': stored_element.get('__meta')
            }

            # send modify request
            self.modify_request(wdir_uuid, element={
                "path": element.get('path', ''),
                "basename": element.get('basename', ''),
                "data": element.get('data')}, **kwargs)

        except Exception as ex:
            logger.error('Update append failed - {}'.format(ex))

    def update_elements(self, stored_element, update_element):
        """
        Update one element with other.

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        stored_element    dict            element stored to update
        update_element    dict            update element
        ================  =============   ====================================
        """
        logger.info("Updating element")

        # LIST stored element
        if (
                (isinstance(stored_element.get('__kern'), list)) and
                (isinstance(update_element.get('data', {}).get('kern'), list))
        ):

            # Check if rowzero is header..
            is_rowzero_header = self.calculate_rowzeroheader_confidence(
                stored_element.get('__meta', {}).get('axisHeaders', {}).get(
                    '*'),  # stored element axisheader
                # stored element first row
                stored_element.get('__kern', [[]])[0]
            )

            # update kern
            stored_element['__kern'] = self.update_arrays_elements(
                original_array=stored_element.get('__kern', {}),
                update_array=update_element.get('data', {}).get('kern', {}),
                is_rowzero_header=is_rowzero_header
            )

            # update meta
            stored_element['__meta'] = self.reload_meta(
                kern=stored_element.get('__kern', {}),
                original_meta=stored_element.get('__meta', {}),
                path_key='',
                is_rowzero_header=is_rowzero_header)

        # DICT stored element
        elif (
                (isinstance(stored_element.get('__kern'), dict)) and
                (isinstance(update_element.get('data', {}).get('kern'), dict))
        ):
            flatten_element_keys = list(flatten(
                update_element.get('data', {}).get('kern'), sep='/').keys())

            element_keys = set(
                [re.split("[0-9]", x)[0] for x in flatten_element_keys])

            # add element
            for element_keypath in element_keys:

                stored_axisheader = stored_element.get('__meta', {}).get(
                    'axisHeaders', {}).get(element_keypath, [])
                stored_first_row = get_element(stored_element.get(
                    '__kern', {}), element_keypath+"/0") or []

                is_rowzero_header = self.calculate_rowzeroheader_confidence(
                    stored_axisheader,
                    stored_first_row
                )

                # update kern
                updated_keypath_array = self.update_arrays_elements(
                    original_array=get_element(stored_element.get(
                        '__kern', {}), element_keypath) or [],
                    update_array=get_element(update_element.get(
                        'data', {}).get('kern', {}), element_keypath),
                    is_rowzero_header=is_rowzero_header
                )

                # Update meta
                updated_keypath_meta = self.reload_meta(
                    kern=updated_keypath_array,
                    original_meta=stored_element.get('__meta', {}),
                    path_key=element_keypath,
                    is_rowzero_header=is_rowzero_header)

                # add updated kern to keypath
                add_element(stored_element.get('__kern', {}),
                            element_keypath,
                            updated_keypath_array,
                            override=True)

                # add updated meta to stored element
                add_element(stored_element,
                            '__meta',
                            updated_keypath_meta,
                            override=True)

        else:
            msg = 'Not compatible type elements to update {} - {}'
            logger.warning(msg.format(
                type(stored_element.get('__kern')).__name__,
                type(update_element.get('data', {}).get('kern')).__name__,))

    def reload_meta(
            self, kern, original_meta, path_key='', is_rowzero_header=False):
        """
        Reload element meta by default, updating axisheaders and dimension.
        ==================   =============   ==================================
        Parameter            Type            Description
        ==================   =============   ==================================
        kern                 dict or list    element kern.
        original_meta        dict            element meta.
        path_key             str             path keys to array in a dict.
        is_rowzero_header    boolean         Rowzero contains array header.
        ==================   =============   ==================================

        Returns:
            (dict) Meta updated data by default using the kern.
        """
        updated_meta = {}
        row_zero = []
        updated_meta.update(original_meta)

        try:
            rows = get_element(
                kern, '/'.join(exclude_empty_values([path_key])))

            if rows:
                row_zero = rows[0] if isinstance(row_zero, list) else rows

                if is_rowzero_header:
                    # Update axisheaders
                    axisheaders = {
                        path_key: [force_list(x)[0] for x in rows],
                        os.path.join(path_key, "*"): row_zero
                    }
                else:
                    top = 1

                    if rows and isinstance(rows[0], list):
                        top = len(row_zero)

                    list_range = range(1, top + 1)

                    header = ['Header{}'.format(x) for x in list_range]

                    axisheaders = {
                        path_key: [force_list(x)[0] for x in rows],
                        os.path.join(path_key, "*"): header
                    }

                add_element(updated_meta, "axisHeaders", axisheaders)

                # Update dimension
                dimension = get_dimension(rows) if path_key else {
                    "": get_dimension(kern)}
                add_element(
                    updated_meta, '/'.join(["dimension", path_key]), dimension)

        except Exception as ex:
            logger.error('Fail reloading meta.. - {}'.format(ex))
            updated_meta = original_meta

        return updated_meta

    @classmethod
    def calculate_rowzeroheader_confidence(
            cls,
            axisheaders,
            row_zero,
            confidence_err=_ROWZEROHEADER_CONFIDENCE_VALUE):
        """
        Calculate the cofidence index if the first row contains headers
        comparing this headers with the axisheaders. If this index is lower
        than the _ROWZERO_HEADER_CONFIDENCE_VALUE we think that the data in
        row_zero doesnt contains headers.
        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        axisheaders       list            list of axisheaders
        rowzero           list            list with firt row of the element.
        ================  =============   ====================================
        Returns:
        (Boolean) if could trust about the rowzero has data headers.
        """
        row_zero_header_confidence = 0

        if axisheaders:
            row_zero_header_confidence = float(
                sum([axisheaders.count(x) for x in row_zero]))/len(axisheaders)

        return row_zero_header_confidence >= confidence_err

    @classmethod
    def merge_headers(cls, header1, header2):
        """
        Merge 2 headers without losing the header 1 order and removing repeated
        elements from header2 in header1.

        =============  ========   ===========================================
        Parameter      Type       Description
        =============  ========   ===========================================
        header1        list       1st element header, must maintain its order
        header2        list       2nd element header
        =============  ========   ===========================================

        Returns:
            (list) merged and ordered headers.
        """

        return remove_list_duplicates(header1 + header2)

    def update_arrays_elements(self, original_array, update_array,
                               is_rowzero_header):
        """
        Update arrays elements
        """
        result = []

        # row zero contains data headers
        if is_rowzero_header:
            merged_headers = self.merge_headers(
                original_array[0], update_array[0])
            result.append(merged_headers)

            for data in original_array[1:]:
                result.append(
                    dict2orderedlist(
                        dict(zip(original_array[0], data)),
                        merged_headers,
                        default=''))

            for data in update_array[1:]:
                result.append(
                    dict2orderedlist(
                        dict(zip(update_array[0], data)),
                        merged_headers,
                        default=''))

        # row zero contains data headers
        else:
            result = original_array
            original_array.extend(update_array)

        return result
