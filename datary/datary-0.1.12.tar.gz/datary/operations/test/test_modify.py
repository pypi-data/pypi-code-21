# -*- coding: utf-8 -*-
"""
Datary python sdk Mofify Operation test file
"""
import mock

from scrapbag import get_dimension
from datary.test.test_datary import DataryTestCase
from datary.test.mock_requests import MockRequestResponse


class DataryModifyOperationTestCase(DataryTestCase):
    """
    ModifyOperation Test case
    """
    @mock.patch('datary.Datary.request')
    def test_modify_request(self, mock_request):
        """
        Test datary operation modify modify_request
        """
        mock_request.return_value = MockRequestResponse("")
        self.datary.modify_request(self.json_repo.get(
            'workdir', {}).get('uuid'), self.element)
        mock_request.return_value = None
        self.datary.modify_request(self.json_repo.get(
            'workdir', {}).get('uuid'), self.element)
        self.assertEqual(mock_request.call_count, 2)

    @mock.patch('datary.Datary.override_file')
    @mock.patch('datary.Datary.update_append_file')
    def test_modify_file(self, mock_update_append, mock_override_file):
        """
        Test datary operation modify modify_file
        """

        mock_mod_style = mock.MagicMock()

        # override mode
        self.datary.modify_file(self.json_repo.get(
            'workdir', {}).get('uuid'), self.element)
        self.datary.modify_file(self.json_repo.get('workdir', {}).get(
            'uuid'), self.element, mod_style='override')
        self.assertEqual(mock_override_file.call_count, 2)

        # update-append mode
        self.datary.modify_file(self.json_repo.get('workdir', {}).get(
            'uuid'), self.element, mod_style='update-append')
        self.assertEqual(mock_update_append.call_count, 1)

        # callable mode
        self.datary.modify_file(self.json_repo.get('workdir', {}).get(
            'uuid'), self.element, mod_style=mock_mod_style)
        self.assertEqual(mock_mod_style.call_count, 1)

        # unexisting mode
        self.datary.modify_file(self.json_repo.get('workdir', {}).get(
            'uuid'), self.element, mod_style="magic-mode")
        self.assertEqual(mock_override_file.call_count, 2)
        self.assertEqual(mock_update_append.call_count, 1)
        self.assertEqual(mock_mod_style.call_count, 1)

    @mock.patch('datary.Datary.modify_request')
    def test_override_file(self, mock_modify_requests):
        """
        Test datary operation modify override_file
        """

        mock_modify_requests.return_value = MockRequestResponse("")
        self.datary.override_file(self.json_repo.get(
            'workdir', {}).get('uuid'), self.element)
        self.assertEqual(mock_modify_requests.call_count, 1)

    @mock.patch('datary.Datary.modify_request')
    @mock.patch('datary.Datary.update_elements')
    @mock.patch('datary.datasets.DataryDatasets.get_original')
    @mock.patch('datary.datasets.DataryDatasets.get_dataset_uuid')
    def test_update_append_file(self, mock_get_dataset_uuid, mock_get_original,
                                mock_update_elements, mock_modify_request):
        """
        Test datary operation modify update_append_file
        """

        # all good.
        mock_get_dataset_uuid.return_value = self.dataset_uuid
        mock_get_original.return_value = self.original

        self.datary.update_append_file(
            wdir_uuid=self.json_repo.get('workdir', {}).get('uuid'),
            element=self.element,
            repo_uuid=self.repo_uuid)

        self.assertEqual(mock_get_dataset_uuid.call_count, 1)
        self.assertEqual(mock_get_original.call_count, 1)
        self.assertEqual(mock_update_elements.call_count, 1)
        self.assertEqual(mock_update_elements.call_count, 1)
        self.assertEqual(mock_modify_request.call_count, 1)

        mock_get_dataset_uuid.reset_mock()
        mock_get_original.reset_mock()
        mock_update_elements.reset_mock()
        mock_update_elements.reset_mock()
        mock_modify_request.reset_mock()

        # Not retrieve orignal case..
        mock_get_original.return_value = None

        self.datary.update_append_file(
            wdir_uuid=self.json_repo.get('workdir', {}).get('uuid'),
            element=self.element,
            repo_uuid=self.repo_uuid)

        self.assertEqual(mock_get_dataset_uuid.call_count, 1)
        self.assertEqual(mock_get_original.call_count, 1)
        self.assertEqual(mock_update_elements.call_count, 0)
        self.assertEqual(mock_update_elements.call_count, 0)
        self.assertEqual(mock_modify_request.call_count, 0)

    @mock.patch('datary.Datary.reload_meta')
    @mock.patch('datary.Datary.update_arrays_elements')
    @mock.patch('datary.Datary.calculate_rowzeroheader_confidence')
    def test_update_elements(self, mock_calculate_rowzeroheader_confidence,
                             mock_update_arrays_elements, mock_reload_meta):
        """
        Test datary operation modify update_elements
        """

        original_dict = {'__kern': {'data_aa': [
            [1, 2, 3]], 'data_b': [[7, 8, 9]]}, '__meta': {}}
        original_list = {'__kern': [[1, 2, 3]], '__meta': {}}

        element_dict = {'path': 'a', 'basename': 'aa', 'data': {'kern': {
            'data_aa': [[4, 5, 6]],
            'data_b': [[7, 8, 9]]}, 'meta': {}}, 'sha1': 'aa_sha1'}

        element_list = {'path': 'a', 'basename': 'aa', 'data': {
            'kern': [[4, 5, 6]], 'meta': {}}, 'sha1': 'aa_sha1'}

        mock_calculate_rowzeroheader_confidence.return_value = True
        mock_update_arrays_elements.return_value = 'kern_updated'
        mock_reload_meta.side_effect = iter([{}, 'meta_reloaded'])

        # case kern dict vs dict
        self.datary.update_elements(original_dict, element_dict)
        self.assertEqual(
            mock_calculate_rowzeroheader_confidence.call_count, 2)
        self.assertEqual(mock_update_arrays_elements.call_count, 2)
        self.assertEqual(mock_reload_meta.call_count, 2)
        self.assertEqual(original_dict.get(
            '__kern').get('data_aa'), 'kern_updated')
        self.assertEqual(original_dict.get('__meta'), 'meta_reloaded')

        mock_calculate_rowzeroheader_confidence.reset_mock()
        mock_update_arrays_elements.reset_mock()
        mock_reload_meta.reset_mock()

        mock_reload_meta.side_effect = iter(['meta_reloaded'])

        self.datary.update_elements(original_list, element_list)

        self.assertEqual(
            mock_calculate_rowzeroheader_confidence.call_count, 1)
        self.assertEqual(mock_update_arrays_elements.call_count, 1)
        self.assertEqual(mock_reload_meta.call_count, 1)
        self.assertEqual(original_list.get('__kern'), 'kern_updated')
        self.assertEqual(original_list.get('__meta'), 'meta_reloaded')

        mock_calculate_rowzeroheader_confidence.reset_mock()
        mock_update_arrays_elements.reset_mock()
        mock_reload_meta.reset_mock()

        # case not permitted log warning
        self.datary.update_elements(self.original, element_list)
        self.assertEqual(
            mock_calculate_rowzeroheader_confidence.call_count, 0)
        self.assertEqual(mock_update_arrays_elements.call_count, 0)
        self.assertEqual(mock_reload_meta.call_count, 0)

    @mock.patch('datary.operations.modify.get_dimension')
    def test_reload_meta(self, mock_get_dimension):
        """
        Test datary operation modify reload_meta
        """

        # false mock
        mock_get_dimension.side_effect = get_dimension

        # kern test data
        kern_with_header = [
            ['H1', 'H2', 'H3'],
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]]

        kern_without_header = kern_with_header[1:]
        kern_dict_with_header = {
            'a': kern_with_header, 'b': kern_with_header[:-1]}
        kern_dict_without_header = {
            'a': kern_with_header[1:],
            'b': kern_with_header[1:-1]}
        kern_array = ['a', 'b', 'c']
        meta_array_init = {'axisHeaders': {
            '': [], '*': []}, 'dimension': {"": [23, 21]}}

        # kern list with header
        meta_with_header = self.datary.reload_meta(
            kern_with_header, {}, path_key='', is_rowzero_header=True)
        self.assertTrue(isinstance(meta_with_header, dict))
        self.assertEqual(meta_with_header.get(
            'axisHeaders', {}).get('*'), ['H1', 'H2', 'H3'])
        self.assertEqual(meta_with_header.get(
            'axisHeaders', {}).get(''), ['H1', 1, 4, 7])
        self.assertEqual(meta_with_header.get('dimension', {}).get(''), [4, 3])

        # kern list without header
        meta_without_header = self.datary.reload_meta(
            kern_without_header, {}, path_key='', is_rowzero_header=False)
        self.assertTrue(isinstance(meta_without_header, dict))
        self.assertEqual(meta_without_header.get('axisHeaders', {}).get(
            '*'), [
                'Header{}'.format(x) for x in range(
                    1, len(kern_with_header[0]) + 1)])
        self.assertEqual(meta_without_header.get(
            'axisHeaders', {}).get(''), [1, 4, 7])
        self.assertEqual(meta_without_header.get(
            'dimension', {}).get(''), [3, 3])

        # kern dict with header
        meta_dict_with_header = self.datary.reload_meta(
            kern_dict_with_header, {}, path_key='a', is_rowzero_header=True)

        self.assertTrue(isinstance(meta_dict_with_header, dict))
        self.assertEqual(meta_dict_with_header.get(
            'axisHeaders', {}).get('a/*'), ['H1', 'H2', 'H3'])
        self.assertEqual(meta_dict_with_header.get(
            'axisHeaders', {}).get('a'), ['H1', 1, 4, 7])
        self.assertEqual(meta_dict_with_header.get(
            'dimension', {}).get('a'), [4, 3])

        # kern dict update meta with other meta
        meta_dict_with_header = self.datary.reload_meta(
            kern_dict_with_header,
            meta_dict_with_header,
            path_key='b', is_rowzero_header=True)

        self.assertTrue(isinstance(meta_dict_with_header, dict))
        self.assertEqual(meta_dict_with_header.get(
            'axisHeaders', {}).get('a/*'), ['H1', 'H2', 'H3'])
        self.assertEqual(meta_dict_with_header.get(
            'axisHeaders', {}).get('a'), ['H1', 1, 4, 7])
        self.assertEqual(meta_dict_with_header.get(
            'axisHeaders', {}).get('b/*'), ['H1', 'H2', 'H3'])
        self.assertEqual(meta_dict_with_header.get(
            'axisHeaders', {}).get('b'), ['H1', 1, 4])
        self.assertEqual(meta_dict_with_header.get(
            'dimension', {}).get('a'), [4, 3])
        self.assertEqual(meta_dict_with_header.get(
            'dimension', {}).get('b'), [3, 3])

        # kern dict without header
        meta_dict_without_header = self.datary.reload_meta(
            kern_dict_without_header,
            {},
            path_key='a',
            is_rowzero_header=False)

        self.assertTrue(isinstance(meta_dict_without_header, dict))
        self.assertEqual(meta_dict_without_header.get('axisHeaders', {}).get(
            'a/*'), [
                'Header{}'.format(x) for x in range(
                    1, len(kern_dict_without_header.get('a')[0]) + 1)])
        self.assertEqual(meta_dict_without_header.get(
            'axisHeaders', {}).get('a'), [1, 4, 7])
        self.assertEqual(meta_dict_without_header.get(
            'dimension', {}).get('a'), [3, 3])

        # kern dict update meta without other meta
        meta_dict_without_header = self.datary.reload_meta(
            kern_dict_without_header,
            meta_dict_without_header,
            path_key='b',
            is_rowzero_header=False)

        self.assertTrue(isinstance(meta_dict_without_header, dict))

        axisheaders = meta_dict_without_header.get('axisHeaders', {})

        self.assertEqual(
            axisheaders.get('a/*'),
            ['Header{}'.format(x) for x in range(
                1, len(kern_dict_without_header.get('a')[0]) + 1)])

        self.assertEqual(meta_dict_without_header.get(
            'axisHeaders', {}).get('a'), [1, 4, 7])
        self.assertEqual(
            axisheaders.get('b/*'),
            ['Header{}'.format(x) for x in range(
                1, len(kern_dict_without_header.get('b')[0]) + 1)])
        self.assertEqual(meta_dict_without_header.get(
            'axisHeaders', {}).get('b'), [1, 4])
        self.assertEqual(meta_dict_without_header.get(
            'dimension', {}).get('a'), [3, 3])
        self.assertEqual(meta_dict_without_header.get(
            'dimension', {}).get('b'), [2, 3])

        # case array and override meta
        meta_array = self.datary.reload_meta(
            kern_array, meta_array_init, path_key='', is_rowzero_header=False)
        self.assertTrue(isinstance(meta_array, dict))
        self.assertEqual(meta_array.get(
            'axisHeaders', {}).get(''), ['a', 'b', 'c'])
        self.assertEqual(meta_array.get(
            'axisHeaders', {}).get('*'), ['Header1'])
        self.assertEqual(meta_array.get('dimension', {}).get(''), [3, 1])

        # test empty rows
        meta_array_empty_rows = self.datary.reload_meta(
            [], meta_array_init, path_key='', is_rowzero_header=False)
        self.assertEqual(isinstance(meta_array_empty_rows, dict), True)
        self.assertEqual(meta_array_empty_rows, meta_array_init)

        # test capture exception
        mock_get_dimension.side_effect = Exception("Test exception")
        meta_array_after_ex = self.datary.reload_meta(
            kern_array, meta_array_init, path_key='', is_rowzero_header=False)
        self.assertEqual(isinstance(meta_array_after_ex, dict), True)
        self.assertEqual(meta_array_after_ex, meta_array_init)

    def test_calculate_rowzeroheader_confidence(self):
        """
        Test datary operation modify calculate_rowzeroheader_confidence
        """

        axisheaders = ['b', 'c', 'a']
        axisheaders2 = ['bb', 'cc', 'a']

        self.assertEqual(self.datary.calculate_rowzeroheader_confidence(
            [], axisheaders), False)
        self.assertEqual(self.datary.calculate_rowzeroheader_confidence(
            axisheaders, axisheaders), True)
        self.assertEqual(self.datary.calculate_rowzeroheader_confidence(
            axisheaders, sorted(axisheaders)), True)
        self.assertEqual(self.datary.calculate_rowzeroheader_confidence(
            axisheaders, axisheaders2), False)
        self.assertEqual(self.datary.calculate_rowzeroheader_confidence(
            axisheaders, axisheaders2, float(1)/3), True)

    def test_merge_headers(self):
        """
        Test datary operation modify merge_headers
        """

        header1 = ['H1', 'H2', 'H3']
        header2 = ['H4', 'H2', 'H1']

        result = self.datary.merge_headers(header1, header2)
        self.assertEqual(result, ['H1', 'H2', 'H3', 'H4'])

        result2 = self.datary.merge_headers(result, ['H5', 'pepe'])
        self.assertEqual(result2, ['H1', 'H2', 'H3', 'H4', 'H5', 'pepe'])

    def test_update_arrays_elements(self):
        """
        Test datary operation modify update_arrays_elements
        """

        kern1 = [['h1', 'h2', 'h3'], [1, 2, 3], [4, 5, 6]]
        kern2 = [['h1', 'h5', 'h7'], [7, 8, 9], [10, 11, 12], [0, 13, 14]]

        result_kern_with_headers = self.datary.update_arrays_elements(
            kern1, kern2, True)
        result_kern_without_headers = self.datary.update_arrays_elements(
            kern1[1:], kern2[1:], False)

        self.assertEqual(isinstance(result_kern_with_headers, list), True)
        self.assertEqual(all([isinstance(x, list)
                              for x in result_kern_with_headers]), True)
        self.assertEqual(
            result_kern_with_headers[0], ['h1', 'h2', 'h3', 'h5', 'h7'])
        self.assertEqual(result_kern_with_headers[-1], [0, '', '', 13, 14])

        self.assertEqual(isinstance(result_kern_without_headers, list), True)
        self.assertEqual(all([isinstance(x, list)
                              for x in result_kern_without_headers]), True)
        self.assertEqual(result_kern_without_headers[0], kern1[1])
        self.assertEqual(result_kern_without_headers[-1], kern2[-1])
