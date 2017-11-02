import pytest

from wscheck.checker import WhitespaceChecker, RULES


class TestExcludingRules(object):
    def test_add_one_exclusion_for_one_issue_type(self):
        checker = WhitespaceChecker(excluded_rules=['WSC001'])
        checker.check_text('apple\r')
        assert [] == checker.issues

    def test_add_one_exclusion_for_two_issue_types(self):
        checker = WhitespaceChecker(excluded_rules=['WSC001'])
        checker.check_text('\tapple\r')
        assert [
            {
                'rule': 'WSC004', 'path': '<string>', 'line': 1, 'col': 1,
                'context': '\tapple', 'message_suffix': None
            },
        ] == checker.issues

    def test_add_two_exclusions_for_one_issue_types(self):
        checker = WhitespaceChecker(excluded_rules=['WSC001', 'WSC004'])
        checker.check_text('apple\r')
        assert [] == checker.issues

    def test_exclude_all_rules_makes_error(self):
        with pytest.raises(RuntimeError) as e:
            WhitespaceChecker(excluded_rules=list(RULES))

        assert 'No rules to check' in str(e)
