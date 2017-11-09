import unittest

from fdutil import dict_tools


class TestFilterDict(unittest.TestCase):

    def setUp(self):
        self.input_dict = {u"e1": {u"API": u"A", u"ENV": u"1", u"PARAMS": u"x, y, z"},
                           u"e2": {u"API": u"B", u"ENV": u"1", u"PARAMS": u"w, x"},
                           u"e3": {u"API": u"B", u"ENV": u"2", u"PARAMS": u"w, x"},
                           u"description1": u"Example environments parameters:",
                           u"description2": u"ENV - The environment to be used",
                           u"description3": u"ENV",
                           u"description4": [u"ENV", u"API", u"PARAM"],
                           u"description5": [u"API", u"PARAM"]
                           }

        self.single_filter = [(u"ENV", u"1")]
        self.single_filter_none = [(u"ENV", None)]
        self.and_filter = [(u'API', u'B'), (u'ENV', u'2', u'AND')]
        self.or_filter = [(u'API', u'B'), (u'ENV', u'2', u'OR')]
        self.multi_filter = [(u'API', u'B'), (u'ENV', u'2', u'AND'), (u'PARAMS', u'x, y, z', u'OR')]
        self.multi_and_filter = [(u'API', None), (u'ENV', u'1', u'AND'), (u'PARAMS', u'w, x', u'AND')]

    def tearDown(self):
        pass

    # happy path tests
    def test_no_filter_exclude_false(self):

        output = dict_tools.filter_dict(src_dict=self.input_dict,
                                        filters=[],
                                        exclude=False)

        # Always nothing
        expected_output = {}

        self.assertEqual(expected_output,
                         output,
                         msg=u'No Filter, exclude=False; Not working as expected')

    def test_no_filter_exclude_true(self):

        output = dict_tools.filter_dict(src_dict=self.input_dict,
                                        filters=[],
                                        exclude=True)

        # Always Everything!
        expected_output = {u"e1": {u"API": u"A", u"ENV": u"1", u"PARAMS": u"x, y, z"},
                           u"e2": {u"API": u"B", u"ENV": u"1", u"PARAMS": u"w, x"},
                           u"e3": {u"API": u"B", u"ENV": u"2", u"PARAMS": u"w, x"},
                           u"description1": u"Example environments parameters:",
                           u"description2": u"ENV - The environment to be used",
                           u"description3": u"ENV",
                           u"description4": [u"ENV", u"API", u"PARAM"],
                           u"description5": [u"API", u"PARAM"]
                           }

        self.assertEqual(expected_output,
                         output,
                         msg=u'No Filter, exclude=True; Not working as expected')

    def test_single_filter_exclude_false(self):

        output = dict_tools.filter_dict(src_dict=self.input_dict,
                                        filters=self.single_filter,
                                        exclude=False)

        expected_output = {u'e1': {u'API': u'A', u'PARAMS': u'x, y, z', u'ENV': u'1'},
                           u'e2': {u'API': u'B', u'PARAMS': u'w, x', u'ENV': u'1'},
                           }

        self.assertEqual(expected_output,
                         output,
                         msg=u'Single Filter, exclude=False; Not working as expected')

    def test_single_filter_exclude_true(self):

        output = dict_tools.filter_dict(src_dict=self.input_dict,
                                        filters=self.single_filter,
                                        exclude=True)

        expected_output = {u"e3": {u"API": u"B", u"ENV": u"2", u"PARAMS": u"w, x"},
                           u"description1": u"Example environments parameters:",
                           u"description2": u"ENV - The environment to be used",
                           u"description3": u"ENV",
                           u"description4": [u"ENV", u"API", u"PARAM"],
                           u"description5": [u"API", u"PARAM"]
                           }

        self.assertEqual(expected_output,
                         output,
                         msg=u'Single Filter, exclude=True; Not working as expected')

    def test_and_filter_exclude_false(self):

        output = dict_tools.filter_dict(src_dict=self.input_dict,
                                        filters=self.and_filter,
                                        exclude=False)

        expected_output = {u"e3": {u"API": u"B", u"ENV": u"2", u"PARAMS": u"w, x"}}

        self.assertEqual(expected_output,
                         output,
                         msg=u'Multiple Filters (AND), exclude=False; Not working as expected')

    def test_and_filter_exclude_true(self):

        output = dict_tools.filter_dict(src_dict=self.input_dict,
                                        filters=self.and_filter,
                                        exclude=True)

        expected_output = {u"e1": {u"API": u"A", u"ENV": u"1", u"PARAMS": u"x, y, z"},
                           u"e2": {u"API": u"B", u"ENV": u"1", u"PARAMS": u"w, x"},
                           u"description1": u"Example environments parameters:",
                           u"description2": u"ENV - The environment to be used",
                           u"description3": u"ENV",
                           u"description4": [u"ENV", u"API", u"PARAM"],
                           u"description5": [u"API", u"PARAM"]
                           }

        self.assertEqual(expected_output,
                         output,
                         msg=u'Multiple Filters (AND), exclude=True; Not working as expected')

    def test_or_filter_exclude_false(self):

        output = dict_tools.filter_dict(src_dict=self.input_dict,
                                        filters=self.or_filter,
                                        exclude=False)

        expected_output = {u"e2": {u"API": u"B", u"ENV": u"1", u"PARAMS": u"w, x"},
                           u"e3": {u"API": u"B", u"ENV": u"2", u"PARAMS": u"w, x"}
                           }

        self.assertEqual(expected_output,
                         output,
                         msg=u'Multiple Filters (OR), exclude=False; Not working as expected')

    def test_or_filter_exclude_true(self):

        output = dict_tools.filter_dict(src_dict=self.input_dict,
                                        filters=self.or_filter,
                                        exclude=True)

        expected_output = {u"e1": {u"API": u"A", u"ENV": u"1", u"PARAMS": u"x, y, z"},
                           u"description1": u"Example environments parameters:",
                           u"description2": u"ENV - The environment to be used",
                           u"description3": u"ENV",
                           u"description4": [u"ENV", u"API", u"PARAM"],
                           u"description5": [u"API", u"PARAM"]
                           }

        self.assertEqual(expected_output,
                         output,
                         msg=u'Multiple Filters (OR), exclude=True; Not working as expected')

    def test_multi_filter_exclude_false(self):

        output = dict_tools.filter_dict(src_dict=self.input_dict,
                                        filters=self.multi_filter,
                                        exclude=False)

        expected_output = {u"e1": {u"API": u"A", u"ENV": u"1", u"PARAMS": u"x, y, z"},
                           u"e3": {u"API": u"B", u"ENV": u"2", u"PARAMS": u"w, x"}
                           }

        self.assertEqual(expected_output,
                         output,
                         msg=u'Multiple Filters (AND + OR), exclude=False; Not working as expected')

    def test_multi_filter_exclude_true(self):

        output = dict_tools.filter_dict(src_dict=self.input_dict,
                                        filters=self.multi_filter,
                                        exclude=True)

        expected_output = {u"e2": {u"API": u"B", u"ENV": u"1", u"PARAMS": u"w, x"},
                           u"description1": u"Example environments parameters:",
                           u"description2": u"ENV - The environment to be used",
                           u"description3": u"ENV",
                           u"description4": [u"ENV", u"API", u"PARAM"],
                           u"description5": [u"API", u"PARAM"]
                           }

        self.assertEqual(expected_output,
                         output,
                         msg=u'Multiple Filters (AND + OR), exclude=True; Not working as expected')

    def test_multi_and_filter_exclude_false(self):

        output = dict_tools.filter_dict(src_dict=self.input_dict,
                                        filters=self.multi_and_filter,
                                        exclude=False)

        expected_output = {u"e2": {u"API": u"B", u"ENV": u"1", u"PARAMS": u"w, x"}}

        self.assertEqual(expected_output,
                         output,
                         msg=u'Multiple Filters (AND + AND), exclude=False; Not working as expected')

    def test_multi_and_filter_exclude_true(self):

        output = dict_tools.filter_dict(src_dict=self.input_dict,
                                        filters=self.multi_and_filter,
                                        exclude=True)

        expected_output = {u"e1": {u"API": u"A", u"ENV": u"1", u"PARAMS": u"x, y, z"},
                           u"e3": {u"API": u"B", u"ENV": u"2", u"PARAMS": u"w, x"},
                           u"description1": u"Example environments parameters:",
                           u"description2": u"ENV - The environment to be used",
                           u"description3": u"ENV",
                           u"description4": [u"ENV", u"API", u"PARAM"],
                           u"description5": [u"API", u"PARAM"]
                           }

        self.assertEqual(expected_output,
                         output,
                         msg=u'Multiple Filters (AND + AND), exclude=True; Not working as expected')

    def test_none_search_value_exclude_false(self):

        output = dict_tools.filter_dict(src_dict=self.input_dict,
                                        filters=self.single_filter_none,
                                        exclude=False)

        expected_output = {u"e1": {u"API": u"A", u"ENV": u"1", u"PARAMS": u"x, y, z"},
                           u"e2": {u"API": u"B", u"ENV": u"1", u"PARAMS": u"w, x"},
                           u"e3": {u"API": u"B", u"ENV": u"2", u"PARAMS": u"w, x"},
                           u"description3": u"ENV",
                           u"description4": [u"ENV", u"API", u"PARAM"],
                           }

        self.assertEqual(expected_output,
                         output,
                         msg=u'None Search Value Filter, exclude=False; Not working as expected')

    def test_none_search_value_exclude_true(self):

        output = dict_tools.filter_dict(src_dict=self.input_dict,
                                        filters=self.single_filter_none,
                                        exclude=True)

        expected_output = {u"description1": u"Example environments parameters:",
                           u"description2": u"ENV - The environment to be used",
                           u"description5": [u"API", u"PARAM"]
                           }

        self.assertEqual(expected_output,
                         output,
                         msg=u'None Search Value Filter, exclude=True; Not working as expected')

    # Unhappy path tests
    def test_src_dict_wrong_type(self):

        with self.assertRaises(AssertionError,
                               msg=u'src_dict wrong type assertion; Not working as expected'):
            _ = dict_tools.filter_dict(src_dict=u'',
                                       filters=[])

    def test_filters_wrong_type(self):

        with self.assertRaises(AssertionError,
                               msg=u'filters wrong type assertion; Not working as expected'):
            _ = dict_tools.filter_dict(src_dict=self.input_dict,
                                       filters=u'')

    def test_first_filter_wrong_type(self):

        with self.assertRaises(AssertionError,
                               msg=u'first filter wrong type assertion; Not working as expected'):
            _ = dict_tools.filter_dict(src_dict=self.input_dict,
                                       filters=[{u''}])

    def test_other_filter_wrong_type(self):

        with self.assertRaises(AssertionError,
                               msg=u'first filter wrong type assertion; Not working as expected'):
            _ = dict_tools.filter_dict(src_dict=self.input_dict,
                                       filters=[(u'ENV', u'1'), {u''}])

    def test_first_filter_missing_param(self):

        with self.assertRaises(AssertionError,
                               msg=u'First filter missing parameter; Not working as expected'):
            _ = dict_tools.filter_dict(src_dict=self.input_dict,
                                       filters=[(u'ENV', )])

    def test_other_filter_missing_param(self):

        with self.assertRaises(AssertionError,
                               msg=u'First filter missing parameter; Not working as expected'):
            _ = dict_tools.filter_dict(src_dict=self.input_dict,
                                       filters=[(u'ENV', u'1'), (u'API', u'A')])

    def test_src_value(self):

        src_dict = self.input_dict.copy()
        src_dict[u'broken'] = tuple()

        with self.assertRaises(TypeError,
                               msg=u'invlaid filter assertion; Not working as expected'):
            _ = dict_tools.filter_dict(src_dict=src_dict,
                                       filters=self.multi_filter)


class TestSortDict(unittest.TestCase):

    def setUp(self):
        self.input_dict = {
            u"description5": [u"API", u"PARAM"],
            u"description1": u"Example environments parameters:",
            u"description3": u"ENV",
            u"description4": [u"ENV", u"API", u"PARAM"],
            u"description2": u"ENV - The environment to be used"
        }

        self.asc_dict = {
            u"description1": u"Example environments parameters:",
            u"description2": u"ENV - The environment to be used",
            u"description3": u"ENV",
            u"description4": [u"ENV", u"API", u"PARAM"],
            u"description5": [u"API", u"PARAM"]
        }

        self.desc_dict = {
            u"description5": [u"API", u"PARAM"],
            u"description4": [u"ENV", u"API", u"PARAM"],
            u"description3": u"ENV",
            u"description2": u"ENV - The environment to be used",
            u"description1": u"Example environments parameters:"
        }

    def tearDown(self):
        pass

    # happy path tests
    def test_sort_ascending(self):

        output = dict_tools.sort_dict(src_dict=self.input_dict)

        self.assertEqual(self.asc_dict,
                         output,
                         msg=u'Sort ascending; Not working as expected')

    def test_sort_descending(self):

        output = dict_tools.sort_dict(src_dict=self.input_dict,
                                      descending=True)

        self.assertEqual(self.desc_dict,
                         output,
                         msg=u'Sort descending; Not working as expected')
