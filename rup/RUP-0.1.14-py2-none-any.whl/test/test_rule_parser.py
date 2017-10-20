import re
from StringIO import StringIO
from unittest import TestCase

from rup import rules


class TestRuleParser(TestCase):

    def test_name_of_first_is_IFA_runs(self):
        stream = StringIO("""
IFA_runs:
    facility: !!python/regexp '^IFA$'
    experiment: !!python/regexp '^IFA$'
    image: munken/unpacker
    raw_path: /tmp/
    unpacked_path: /tmp/
        """)

        r = rules.parse_rules(stream)

        self.assertEqual("IFA_runs", r[0].name)

    def test_image_of_first_is_munken_unpacker(self):
        stream = StringIO("""
        IFA_runs:
            facility: !!python/regexp '^IFA$'
            experiment: !!python/regexp '^IFA$'
            image: munken/unpacker
            raw_path: /tmp/
            unpacked_path: /tmp/
                    """)

        r = rules.parse_rules(stream)

        self.assertEqual("munken/unpacker", r[0].image)

    def test_facility_is_regexp_that_matches_IFA(self):
        stream = StringIO("""
            IFA_runs:
                facility: !!python/regexp '^IFA$'
                experiment: !!python/regexp '^IFA$'
                image: munken/unpacker
                raw_path: /tmp/
                unpacked_path: /tmp/
                                """)

        r = rules.parse_rules(stream)

        self.assertEqual(re.compile(r"^IFA$").pattern, r[0].facility.pattern)

    def test_experiment_is_regexp_that_matches_IFA(self):
        stream = StringIO("""
            IFA_runs:
                facility: !!python/regexp '^IFA$'
                experiment: !!python/regexp '^IFA$'
                image: munken/unpacker
                raw_path: /tmp/
                unpacked_path: /tmp/
                    """)

        r = rules.parse_rules(stream)

        self.assertEqual(re.compile(r"^IFA$").pattern, r[0].experiment.pattern)

    def test_the_order_of_the_input_is_preserved(self):
        stream = StringIO("""
IFA_runs:
    facility: !!python/regexp '^IFA$'
    experiment: !!python/regexp '^IFA$'
    image: munken/unpacker
    raw_path: /tmp/
    unpacked_path: /tmp/

Runs2:
    facility: !!python/regexp '^IFA$'
    experiment: !!python/regexp '^IFA$'
    image: munken/unpacker
    raw_path: /tmp/
    unpacked_path: /tmp/
""")

        r = rules.parse_rules(stream)

        self.assertEqual(2, len(r))
        self.assertEqual("IFA_runs", r[0].name)
        self.assertEqual("Runs2", r[1].name)