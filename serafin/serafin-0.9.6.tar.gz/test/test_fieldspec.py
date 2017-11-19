# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,unsubscriptable-object
from __future__ import absolute_import, unicode_literals

# stdlib imports
from unittest import TestCase

# local imports
from serafin.fieldspec import Fieldspec


class FieldspecTest(TestCase):
    def setUp(self):
        self.spec = Fieldspec('field1,field2(sub1,sub2),field3(*)')

    def test_creation(self):
        self.assertEqual(repr(self.spec), '<Fieldspec: field1,field2,field3>')

    def test_contains(self):
        self.assertIn('field1', self.spec)
        self.assertNotIn('field7', self.spec)

    def test_get_subspec(self):
        self.assertEqual(self.spec['field1'], True)

        self.assertEqual(repr(self.spec['field2']), '<Fieldspec: sub1,sub2>')
        self.assertEqual(self.spec['field2']['sub1'], True)
        self.assertIn('sub1', self.spec['field2'])

    def test_return_proper_for_star_fieldspec(self):
        spec = Fieldspec('*')
        self.assertTrue('test' in spec)
        self.assertTrue(spec['test'])

    def test_raises_ValueError_when_invalid_symbols_are_used_in_the_spec(self):
        invalid = ['!@#$%^&[]{}:"\';\\<>,./?']
        for ch in invalid:
            with self.assertRaises(ValueError):
                Fieldspec(ch)

    def test_raises_ValueError_when_unmatched_opening_parenthesis(self):
        with self.assertRaises(ValueError):
            Fieldspec('test(,test2')

        with self.assertRaises(ValueError):
            Fieldspec('test(ttt,adsf(one),test2')

    def test_raises_ValueError_when_unmatched_closing_parenthesis(self):
        with self.assertRaises(ValueError):
            Fieldspec('test(,test2')

        with self.assertRaises(ValueError):
            Fieldspec('test,ttt,adsf(one)),test2')


class TestMerge(TestCase):
    def test_merge_flat_specs(self):
        spec = Fieldspec('field1,field2')
        spec.merge(Fieldspec('field3,field4'))

        self.assertIn('field1', spec)
        self.assertIn('field2', spec)
        self.assertIn('field3', spec)
        self.assertIn('field4', spec)

    def test_merge_simple_compound_specs(self):
        spec = Fieldspec('field1(field2)')
        spec.merge(Fieldspec('field3(field4)'))

        self.assertIn('field1', spec)
        self.assertIn('field3', spec)
        self.assertIn('field2', spec['field1'])
        self.assertIn('field4', spec['field3'])

        self.assertNotIn('field2', spec)
        self.assertNotIn('field4', spec)

    def test_field_in_one_and_excluded_in_other_is_present_in_merge(self):
        merged = Fieldspec('field1,field2,-field3').merge('field2,field3')
        self.assertIn('field1', merged)
        self.assertIn('field2', merged)
        self.assertIn('field3', merged)

    def test_field_in_one_and_excluded_in_other_is_present_in_merge_2(self):
        merged = Fieldspec('field2,field3').merge('field1,field2,-field3')
        self.assertIn('field1', merged)
        self.assertIn('field2', merged)
        self.assertIn('field3', merged)

    def test_field_in_one_and_excluded_in_other_is_present_in_merge_3(self):
        merged = Fieldspec('field2,field3').merge('*,-field3')
        self.assertIn('field1', merged)
        self.assertIn('field2', merged)
        self.assertIn('field3', merged)
        self.assertIn('field99', merged)

    def test_field_excluded_in_both_is_excluded_in_merge(self):
        merged = Fieldspec('field1,field2,-field3').merge('field2,-field3')
        self.assertIn('field1', merged)
        self.assertIn('field2', merged)
        self.assertNotIn('field3', merged)

    def test_field_excluded_in_both_is_excluded_in_merge_2(self):
        merged = Fieldspec('*,-field3').merge('*,-field3')
        self.assertIn('field1', merged)
        self.assertIn('field2', merged)
        self.assertNotIn('field3', merged)
        self.assertIn('field99', merged)


class TestMergeConfict(TestCase):
    def test_merge_simple_fields(self):
        spec = Fieldspec('field1,field2')
        spec.merge(Fieldspec('field2,field3'))

        self.assertEqual(spec.all, False)
        self.assertIn('field1', spec)
        self.assertIn('field2', spec)
        self.assertIn('field3', spec)

    def test_merge_two_fieldspecs(self):
        spec = Fieldspec('field1(field2)')
        spec.merge(Fieldspec('field1(field3)'))

        self.assertEqual(spec.all, False)

        self.assertNotIn('field2', spec)
        self.assertNotIn('field3', spec)

        self.assertIn('field1', spec)
        self.assertIn('field2', spec['field1'])
        self.assertIn('field3', spec['field1'])

    def test_merge_subspec_and_simple_field(self):
        spec = Fieldspec('field1(field2)')
        spec.merge(Fieldspec('field1,field3'))

        self.assertEqual(spec.all, False)

        self.assertIn('field1', spec)
        self.assertIn('field3', spec)
        self.assertIn('field2', spec['field1'])

        self.assertNotIn('field2', spec)

    def test_merge_subspec_and_all(self):
        spec = Fieldspec('field1(field2)')
        spec.merge(Fieldspec('field1(*)'))

        self.assertIn('field1', spec)
        self.assertIn('field99', spec['field1'])

        self.assertNotIn('field2', spec)
        self.assertNotIn('field4', spec)

        self.assertEqual(spec['field1'].all, True)
        self.assertEqual(spec['field1']['asdf'], True)

    def test_merge_simple_field_and_subspec(self):
        spec = Fieldspec('field1,field3')
        spec.merge(Fieldspec('field1(field2)'))

        self.assertEqual(spec.all, False)

        self.assertIn('field1', spec)
        self.assertIn('field3', spec)
        self.assertIn('field2', spec['field1'])

        self.assertNotIn('field2', spec)

    def test_merge_simple_field_and_subspec2(self):
        spec = Fieldspec('field1(field2)')
        spec.merge(Fieldspec('field1,field3'))

        self.assertEqual(spec.all, False)

        self.assertIn('field1', spec)
        self.assertIn('field3', spec)
        self.assertIn('field2', spec['field1'])

        self.assertNotIn('field2', spec)

    def test_merge_all_and_subspec(self):
        spec = Fieldspec('field1(*)')
        spec.merge(Fieldspec('field1(field2)'))

        self.assertIn('field1', spec)
        self.assertIn('field99', spec['field1'])

        self.assertNotIn('field2', spec)
        self.assertNotIn('field4', spec)

        self.assertEqual(spec['field1'].all, True)
        self.assertEqual(spec['field1']['asdf'], True)

    def test_merge_multiple_conflicts(self):
        spec = Fieldspec('field1(*),field2,field3(field31,field32)')
        spec.merge(Fieldspec('field1(field11),field3(field32,field33),field4'))

        self.assertIn('field1', spec)
        self.assertIn('field2', spec)
        self.assertIn('field3', spec)
        self.assertIn('field4', spec)

        self.assertEqual(spec['field1'].all, True)
        self.assertIn('field12', spec['field1'])
        self.assertIn('field11', spec['field1'])
        self.assertIn('asdf', spec['field1'])

        self.assertIn('field31', spec['field3'])
        self.assertIn('field32', spec['field3'])
        self.assertIn('field33', spec['field3'])

    def test_merge_nested_fieldspec(self):
        spec = Fieldspec('field1(field11,field12(field111,field112))')
        other = Fieldspec('field1(field12(field112,field113),field13)')
        spec.merge(other)

        self.assertIn('field1', spec)
        self.assertIn('field11', spec['field1'])
        self.assertIn('field12', spec['field1'])
        self.assertIn('field13', spec['field1'])

        subspec = spec['field1']['field12']
        self.assertIn('field111', subspec)
        self.assertIn('field112', subspec)
        self.assertIn('field113', subspec)


class TestRestrict(TestCase):
    def test_simple_fields(self):
        spec = Fieldspec('field1,field2,field3')
        other = Fieldspec('field2,field3')
        restricted = Fieldspec(spec).restrict(other)

        self.assertNotIn('field1', restricted)
        self.assertIn('field2', restricted)
        self.assertIn('field3', restricted)

    def test_simple_fields_with_exclude(self):
        spec = Fieldspec('field1,field2,field3')
        other = Fieldspec('field2,-field3')
        restricted = Fieldspec(spec).restrict(other)

        self.assertIn('field2', restricted)
        self.assertNotIn('field1', restricted)
        self.assertNotIn('field3', restricted)

    def test_excluded_fields_are_not_exposed_after_restrict(self):
        spec = Fieldspec('field1,field2,-field3')
        other = Fieldspec('field2,field3')
        restricted = Fieldspec(spec).restrict(other)

        self.assertIn('field2', restricted)
        self.assertNotIn('field1', restricted)
        self.assertNotIn('field3', restricted)

    def test_restrict_all(self):
        spec = Fieldspec('*')
        other = Fieldspec('field2,field3')
        restricted = Fieldspec(spec).restrict(other)

        self.assertIn('field2', restricted)
        self.assertIn('field3', restricted)
        self.assertNotIn('field1', restricted)

    def test_restrict_all_with_exclusions(self):
        spec = Fieldspec('*,-field1')
        other = Fieldspec('*,-field4')
        restricted = Fieldspec(spec).restrict(other)

        self.assertIn('field2', restricted)
        self.assertIn('field3', restricted)
        self.assertNotIn('field1', restricted)
        self.assertNotIn('field4', restricted)
        self.assertTrue(restricted.all)

    def test_regression_leaking_all_to_result(self):
        spec = Fieldspec('*,columns(name)')
        other = Fieldspec('id,name')
        restricted = Fieldspec(spec).restrict(other)

        self.assertIn('id', restricted)
        self.assertIn('name', restricted)
        self.assertNotIn('columns', restricted)
        self.assertNotIn('*', restricted)
        self.assertFalse(restricted.all)

    def test_regression_properly_limit_sub_specs(self):
        spec = Fieldspec('*,phone_numbers(number)')
        other = Fieldspec('type,phone_numbers(active,mobile,number)')
        restricted = spec.restrict(other)

        self.assertIn('type', restricted)
        self.assertNotIn('foo', restricted)

        subspec = restricted['phone_numbers']
        self.assertIn('number', subspec)
        self.assertNotIn('active', subspec)
        self.assertNotIn('mobile', subspec)


class TestRestrictWithConflicts(TestCase):
    def test_fieldspec_and_field(self):
        spec = Fieldspec('field1(field11,field12,field13)')
        other = Fieldspec('field1')
        restricted = Fieldspec(spec).restrict(other)

        self.assertEqual(restricted['field1'], True)

    def test_one_level_deep(self):
        spec = Fieldspec('field1(field11,field12,field13)')
        other = Fieldspec('field1(field12,-field13)')
        restricted = Fieldspec(spec).restrict(other)

        subspec = restricted['field1']
        self.assertIn('field12', subspec)
        self.assertNotIn('field11', subspec)
        self.assertNotIn('field13', subspec)

    def test_restrict_by_all_with_exclude(self):
        spec = Fieldspec('field1(field11,field12,field13)')
        other = Fieldspec('field1(*,-field13)')
        restricted = Fieldspec(spec)
        restricted.restrict(other)

        subspec = restricted['field1']
        self.assertIn('field11', subspec)
        self.assertIn('field12', subspec)
        self.assertNotIn('field13', subspec)
