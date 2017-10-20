from StringIO import StringIO
from unittest import TestCase

from rup import rules


class TestRuleParser(TestCase):

    def test_simple_rule_matches_IFA(self):
        stream = StringIO("""
IFA_runs:
    facility: !!python/regexp '^IFA$'
    experiment: !!python/regexp '^IFA$'
    image: munken/unpacker
    raw_path: /tmp/
    unpacked_path: /tmp/
        """)

        r = rules.parse_rules(stream)[0]

        rup = {
            'facility': 'IFA',
            'experiment': 'IFA'
        }

        self.assertTrue(r.matches(rup))


    def test_simple_rule_does_not_match_IFA2(self):
        stream = StringIO("""
IFA_runs:
    facility: !!python/regexp '^IFA$'
    experiment: !!python/regexp '^IFA$'
    image: munken/unpacker
    raw_path: /tmp/
    unpacked_path: /tmp/
            """)

        r = rules.parse_rules(stream)[0]

        rup = {
            'facility': 'IFA2',
            'experiment': 'IFA2'
        }

        self.assertFalse(r.matches(rup))

    def test_matching_is_done_on_facility(self):
        stream = StringIO("""
IFA_runs:
    facility: !!python/regexp '^IFA$'
    experiment: !!python/regexp '^IFA$'
    image: munken/unpacker
    raw_path: /tmp/
    unpacked_path: /tmp/
        """)

        r = rules.parse_rules(stream)[0]

        rup = {
            'facility': 'IFA2',
            'experiment': 'IFA'
        }

        self.assertFalse(r.matches(rup))

    def test_matching_is_done_on_experiments(self):
        stream = StringIO("""
IFA_runs:
    facility: !!python/regexp '^IFA$'
    experiment: !!python/regexp '^IFA$'
    image: munken/unpacker
    raw_path: /tmp/
    unpacked_path: /tmp/
        """)

        r = rules.parse_rules(stream)[0]

        rup = {
            'facility': 'IFA',
            'experiment': 'IFA2'
        }

        self.assertFalse(r.matches(rup))

    def test_wildcard_expansion_is_done(self):
        stream = StringIO("""
IFA_runs:
    facility: !!python/regexp '^IFA$'
    experiment: !!python/regexp '^IFA\d+$'
    image: munken/unpacker
    raw_path: /tmp/
    unpacked_path: /tmp/
        """)

        r = rules.parse_rules(stream)[0]

        self.assertTrue(r.matches({
            'facility': 'IFA',
            'experiment': 'IFA2'
        }))

        self.assertFalse(r.matches({
            'facility': 'IFA',
            'experiment': 'IFAD'
        }))