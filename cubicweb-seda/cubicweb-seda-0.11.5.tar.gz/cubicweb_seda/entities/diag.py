# copyright 2016-2017 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-seda tools to diagnose versions compatibility of profiles."""

from collections import namedtuple

from cubicweb import _
from cubicweb.view import EntityAdapter
from cubicweb.predicates import is_instance


ALL_FORMATS = frozenset(('SEDA 2.0', 'SEDA 1.0', 'SEDA 0.2', 'simplified'))

Rule = namedtuple('Rule', ['impacted_formats', 'message', 'tab_id', 'watch'])
RULES = {
    'use_archive_unit_ref': Rule(
        set(['SEDA 1.0', 'SEDA 0.2', 'simplified']),
        _("Archive unit reference are only supported by SEDA 2."),
        'main_tab',
        set([
            'seda_seq_access_rule_rule',
            'seda_seq_appraisal_rule_rule',
        ])),

    'seda1_need_access_rule': Rule(
        set(['SEDA 1.0']),
        _("First level archive unit must have an associated access rule to be exportable "
          "in SEDA 1. You may define it on the archive unit or as a default rule on the "
          "transfer."),
        'seda_management_tab',
        set([
            'seda_archive_unit',
            'seda_alt_archive_unit_archive_unit_ref_id',
            'seda_seq_alt_archive_unit_archive_unit_ref_id_management',
            'seda_access_rule',
        ])),
    'rule_without_rule': Rule(
        set(['SEDA 1.0', 'SEDA 0.2', 'simplified']),
        _("Some management rule has no inner rule, one is required."),
        'seda_management_tab',
        set([
            'seda_seq_access_rule_rule',
            'seda_seq_appraisal_rule_rule',
        ])),
    'rule_with_too_much_rules': Rule(
        set(['SEDA 1.0', 'SEDA 0.2', 'simplified']),
        _("Some management rule has more than one inner rules, a single one is required."),
        'seda_management_tab',
        set([
            'seda_seq_access_rule_rule',
            'seda_seq_appraisal_rule_rule',
        ])),
    'rule_unsupported_card': Rule(
        set(['SEDA 1.0', 'SEDA 0.2', 'simplified']),
        _("Inner rule has cardinality other than 1."),
        'seda_management_tab',
        set([
            ('SEDASeqAccessRuleRule', 'user_cardinality'),
            ('SEDASeqAppraisalRuleRule', 'user_cardinality'),
        ])),
    'rule_need_start_date': Rule(
        set(['SEDA 1.0', 'SEDA 0.2', 'simplified']),
        _("Inner rule has no start date."),
        'seda_management_tab',
        set([
            'seda_start_date',
        ])),
    'rule_start_unsupported_card': Rule(
        set(['SEDA 1.0', 'SEDA 0.2', 'simplified']),
        _("Start date has cardinality other than 1."),
        'seda_management_tab',
        set([
            ('SEDAStartDate', 'user_cardinality'),
        ])),
    'rule_ref_non_rule_id': Rule(
        set(['SEDA 1.0', 'SEDA 0.2', 'simplified']),
        _("Rule has an explicit rule deactivation - only ignore all rules is supported in "
          "simplified profiles."),
        'seda_management_tab',
        set([
            'seda_ref_non_rule_id_from',
        ])),

    'seda02_custodial_history_items': Rule(
        set(['SEDA 0.2']),
        _("Custodial history is text with SEDA 0.2, hence only one item element is considered."),
        'seda_history_tab',
        set([
            'seda_custodial_history_item',
        ])),
    'seda02_custodial_history_when': Rule(
        set(['SEDA 0.2']),
        _("Custodial history is text with SEDA 0.2, hence date information isn't considered."),
        'seda_history_tab',
        set([
            'seda_when',
        ])),
}


class CompatError(namedtuple('_CompatError', ['impacted_formats', 'message', 'tab_id', 'entity'])):
    """Convenience class holding information about a problem in a profile forbidding export to some
    format:

    * `impacted_formats`: set of formats that are no more available because of this error,
    * `message`: message string explaining the problem,
    * `entity`: 1st class entity where the error lies (one of archive unit, data object, etc.),
    * `tab`: entity's tab where the problem may be fixed.
    """
    def __new__(cls, rule_id, entity):
        rule = RULES[rule_id]
        return super(CompatError, cls).__new__(cls, rule.impacted_formats, rule.message,
                                               rule.tab_id, entity)


class ISEDACompatAnalyzer(EntityAdapter):
    """Adapter that will analyze profile to diagnose its format compatibility (SEDA 2, SEDA 1 and/or
    SEDA 0.2) while being to explain the problem to end-users.
    """

    __regid__ = 'ISEDACompatAnalyzer'
    __select__ = is_instance('SEDAArchiveTransfer')

    def diagnose(self):
        possible_formats = set(ALL_FORMATS)
        for compat_error in self.detect_problems():
            possible_formats -= compat_error.impacted_formats
        return possible_formats

    def detect_problems(self):
        """Yield :class:`CompatError` describing a problem that prevents the given profile to be
        compatible with some format.
        """
        for rule_id, entity in self.failing_rules():
            yield CompatError(rule_id, entity)

    def failing_rules(self):
        """Yield (rule identifier, problematic entity) describing a problem that prevents the given
        profile to be compatible with some format.
        """
        for check_method in (self._check_usage_of_reference_archive_unit,
                             self._check_management_rules,
                             self._check_custodial_history_rules):
            for problem in check_method():
                yield problem

    def _check_management_rules(self):  # noqa (too complex)
        profile = self.entity
        # First level archive unit needs an access rule (SEDA 1)
        if not profile.reverse_seda_access_rule:
            for archive_unit in profile.archive_units:
                seq = archive_unit.first_level_choice.content_sequence
                if seq is None:
                    # reference archive unit
                    continue
                if not seq.reverse_seda_access_rule:
                    yield 'seda1_need_access_rule', archive_unit
        # Access/appraisal rule must have one and only one sequence, which have one and only one
        # start date (and both of them must have 1 cardinality)
        for rule in self._cw.execute(
                'Any X WHERE X is IN (SEDAAccessRule, SEDAAppraisalRule), '
                'X container C, C eid %(c)s', {'c': profile.eid}).entities():
            if not rule.rules:
                yield 'rule_without_rule', _parent(rule)
            elif len(rule.rules) > 1:
                yield 'rule_with_too_much_rules', _parent(rule)
            else:
                rule_seq = rule.rules[0]
                if rule_seq.user_cardinality != '1':
                    yield 'rule_unsupported_card', _parent(rule)
                if not rule_seq.start_date:
                    yield 'rule_need_start_date', _parent(rule)
                elif rule_seq.start_date.user_cardinality != '1':
                    yield 'rule_start_unsupported_card', _parent(rule)
        # Access/appraisal rule shouldn't use ref non rule id
        for rule_type in ('access', 'appraisal'):
            for rule in self._cw.execute(
                    'DISTINCT Any X WHERE X seda_alt_{0}_rule_prevent_inheritance ALT,'
                    'REF seda_ref_non_rule_id_from ALT, '
                    'X container C, C eid %(c)s'.format(rule_type),
                    {'c': profile.eid}).entities():
                yield 'rule_ref_non_rule_id', _parent(rule)

    def _check_custodial_history_rules(self):
        profile = self.entity
        # Check for more than one custodial history items (SEDA 0.2)
        for content in self._cw.execute(
                'Any CONT GROUPBY CONT WHERE X seda_custodial_history_item CONT,'
                'X container C, C eid %(c)s HAVING COUNT(X) > 1',
                {'c': profile.eid}).entities():
            parent = _parent(content) if profile.simplified_profile else content
            yield 'seda02_custodial_history_items', parent
        # Check for SEDAwhen usage (SEDA 0.2)
        for content in self._cw.execute(
                'DISTINCT Any CONT WHERE X seda_custodial_history_item CONT,'
                'W seda_when X, X container C, C eid %(c)s',
                {'c': profile.eid}).entities():
            parent = _parent(content) if profile.simplified_profile else content
            yield 'seda02_custodial_history_when', parent

    def _check_usage_of_reference_archive_unit(self):
        for archive_unit in self._cw.execute(
                'DISTINCT Any X WHERE X is SEDAArchiveUnit,'
                'X seda_alt_archive_unit_archive_unit_ref_id ALT, '
                'NOT EXISTS(ALT seda_seq_alt_archive_unit_archive_unit_ref_id_management SEQ),'
                'X container C, C eid %(c)s', {'c': self.entity.eid}).entities():
            yield 'use_archive_unit_ref', archive_unit

    # XXX more than one items ->


def _parent(entity):
    """Return the first encountered parent which is an ArchiveUnit"""
    while entity.cw_etype not in ('SEDAArchiveTransfer', 'SEDAArchiveUnit'):
        entity = entity.cw_adapt_to('IContained').parent
    return entity
