from StringIO import StringIO
from unittest import TestCase

from rup import rules


class TestRuleParser(TestCase):

    def test_dollar_experiment_is_replaced_with_experiment_name(self):
        stream = StringIO("""
IFA_runs:
    facility: !!python/regexp '^IFA$'
    experiment: !!python/regexp '^IFA$'
    image: munken/unpacker
    raw_path: /tmp/
    unpacked_path: /tmp/$experiment
        """)

        r = rules.parse_rules(stream)[0]

        self.assertEqual('/tmp/IFA001', r.unpacked_path('IFA001', 'IFA'))


    def test_dollar_facility_is_replaced_with_facility_name(self):
        stream = StringIO("""
IFA_runs:
    facility: !!python/regexp '^IFA$'
    experiment: !!python/regexp '^IFA$'
    image: munken/unpacker
    raw_path: /tmp/
    unpacked_path: /tmp/$facility
        """)

        r = rules.parse_rules(stream)[0]

        self.assertEqual('/tmp/IFA', r.unpacked_path('IFA001', 'IFA'))


    def test_raw_dollar_experiment_is_replaced_with_experiment_name(self):
        stream = StringIO("""
IFA_runs:
    facility: !!python/regexp '^IFA$'
    experiment: !!python/regexp '^IFA$'
    image: munken/unpacker
    raw_path: /tmp/$experiment
    unpacked_path: /tmp/
        """)

        r = rules.parse_rules(stream)[0]

        self.assertEqual('/tmp/IFA001', r.raw_path('IFA001', 'IFA'))


    def test_raw_dollar_facility_is_replaced_with_facility_name(self):
        stream = StringIO("""
IFA_runs:
    facility: !!python/regexp '^IFA$'
    experiment: !!python/regexp '^IFA$'
    image: munken/unpacker
    raw_path: /tmp/$facility
    unpacked_path: /tmp/
        """)

        r = rules.parse_rules(stream)[0]

        self.assertEqual('/tmp/IFA', r.raw_path('IFA001', 'IFA'))