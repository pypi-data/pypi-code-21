from unittest import TestCase


class TestAclcleanup(TestCase):
    def test_aclcleanup(self):
        g = [{'Grantee': {'DisplayName': 'test',
                          'ID': '3a45dc20-d4d3-4539-a7bc-8f7d084772ea',
                          'Type': 'CanonicalUser'},
              'Permission': 'FULL_CONTROL'}]
        o = {'Owner': {'DisplayName': 'test',
                       'ID': '3a45dc20-d4d3-4539-a7bc-8f7d084772ea'}}

        from hs3shp.parse import aclcleanup
        _o, _g = aclcleanup(o, g)

        from collections import OrderedDict
        self.assertTrue(type(_o) == OrderedDict)
        for i in _g:
            self.assertTrue(type(i) == OrderedDict)

