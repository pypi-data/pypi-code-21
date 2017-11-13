# coding=utf-8
import logging

import six

from .luqum.tree import OrOperation, Word
from .luqum.utils import LuceneTreeVisitorV2, UnknownOperationResolver
from .luqum.parser import parser, lexer
import pyparsing as pp


def process_vals(t, l):
    res = []
    for val in t:
        res.append(l(val))

    return res


def convert_number(t):
    def int_or_float(val):
        if '.' in val:
            return float(val)

        return int(val)

    return process_vals(t, int_or_float)


def parse_expr(expr_text):
    operator = pp.Regex(">=|<=|!=|>|<|=")('operator')

    point = pp.Literal('.')
    e = pp.CaselessLiteral('E')
    plus_or_minus = pp.Literal('+') | pp.Literal('-')
    number = pp.Word(pp.nums)
    integer = pp.Combine(pp.Optional(plus_or_minus) + number)
    float_number = pp.Combine(integer + pp.Optional(point + pp.Optional(number)) + pp.Optional(e + integer))

    float_number.setParseAction(convert_number)

    quoted_string = pp.QuotedString('"')
    identifier = pp.Word(pp.alphanums + "_" + "." + "-")
    text_identifier = (quoted_string | identifier)
    comparison_term = float_number | text_identifier
    values = pp.OneOrMore(comparison_term)('values')
    range_op = pp.Suppress(pp.CaselessLiteral('TO'))
    range_operator = (pp.Suppress('[') + comparison_term + range_op + comparison_term + pp.Suppress(']'))('range')
    range_inclusive = (pp.Suppress('{') + comparison_term + range_op + comparison_term + pp.Suppress('}'))('range_inclusive')

    condition_group = pp.Group((range_inclusive | range_operator | values | (operator + values)))('condition_group')
    conditions = pp.Group(condition_group)('conditions')

    expr = pp.infixNotation(conditions, [
        ("AND", 2, pp.opAssoc.LEFT,),
        ("OR", 2, pp.opAssoc.LEFT,),
    ])

    return expr.parseString(expr_text)


def __conditions_expr_to_sql_where(field_name, item):
    return '({sql})'.format(sql=expr_to_sql_where(field_name, item))


def quotes_if_needed(val):
    return '"%s"' % val if isinstance(val, six.string_types) else val


def __condition_group_expr_to_sql_where(field_name, item):
    if 'values' in item:
        values = item.get('values')
        operator = item.get('operator', '=')
        vals = []
        for val in values:
            vals.append('{field_name}{operator}{value}'.format(
                field_name=field_name, operator=operator, value=quotes_if_needed(val)))

        return 'OR'.join(vals)

    if 'range' in item:
        return ('({field_name}>={value1})AND({field_name}<={value2})'.format(
            field_name=field_name, value1=item[0], value2=item[1]))

    if 'range_inclusive' in item:
        return ('({field_name}>{value1})AND({field_name}<{value2})'.format(
            field_name=field_name, value1=item[0], value2=item[1]))


def expr_to_sql_where(field_name, expr):
    sql = ''
    for item in expr:
        if item.getName() == 'conditions':
            sql += __conditions_expr_to_sql_where(field_name, item)
        elif item.getName() == 'condition_group':
            sql += __condition_group_expr_to_sql_where(field_name, item)

    return sql


class SQLQueryBuilder(LuceneTreeVisitorV2):
    def __init__(self, sql_helper):
        self.__where = {}
        self.__limit = []
        self.__vars = {}
        self.__sql_helper = sql_helper

    def __handle_internal_function(self, node):
        if node.name.lower() == 'sample':
            sample = 1.0 - float(node.expr.value)

            random_function = self.__sql_helper.random_function_name()

            self.__where.setdefault(1, []).append(('AND', '({random_function}>{sample:.4g})'.format(random_function=random_function, sample=sample)))
            return True

        if node.name.lower() == 'seed':
            self.__vars['seed'] = int(str(node.expr))
            return True

        if node.name.lower() == 'split':
            split_vars = node.name.split(':')
            split_vars = map(float, split_vars[1:])

            split = zip(('train', 'test', 'validation'), split_vars)
            self.__vars.update(get_split_vars(split))

            return True

        if node.name.lower() == 'version':
            self.__vars['version'] = str(node.expr)
            return True

        if node.name.lower() == 'limit':
            self.__vars['limit'] = int(str(node.expr))
            return True

    def visit_group(self, node, parents, context):
        self._sub_visit(node.expr, None, is_group=True)

    def visit_prohibit(self, node, parents, context):
        self.__add_where(context.get('field_name'), str(node), context.get('op'))

    def visit_phrase(self, node, parents, context):
        phrase = str(node)

        phrase = phrase.strip()

        self.__add_where(context.get('field_name'), phrase, context.get('op'))

    def visit_range(self, node, parents, context):
        self.__add_where(context.get('field_name'), str(node), context.get('op'))

    def visit_plus(self, node, parents, context):
        self.__add_where(context.get('field_name'), str(node)[1:], context.get('op'))

    def visit_field_group(self, node, parents, context):
        self.visit(node.expr, parents + [node], context)

    def __add_where(self, field_name, expr, op):
        if expr is None:
            self.__where.setdefault(0, []).append((None, '%s is NULL' % field_name))
            return

        where = expr_to_sql_where(field_name, parse_expr(expr))
        self.__where.setdefault(0, []).append((op, where))

    def visit_word(self, node, parents, context):
        self.__add_where(context.get('field_name'), str(node), context.get('op'))

    def visit_search_field(self, node, parents, context):
        if self.__handle_internal_function(node):
            return

        context = context or {}

        for child in node.children:
            if isinstance(child, Word):
                value = str(node.expr)
                if value.lower() == 'null':
                    self.__add_where(node.name, None, 'is')
                else:
                    self.__add_where(node.name, value, context.get('op'))
            else:
                self._sub_visit(node.expr, None, context={'field_name': node.name})

    @classmethod
    def __combine_where(cls, op, sql_builder):
        combine_where = {}
        for bucket, wheres in sorted(sql_builder.where.items()):
            for where in wheres:
                operator, expr = where
                operator = operator or op

                combine_where.setdefault(bucket, []).append((operator, expr))

        return combine_where

    def _sub_visit(self, child, op, context=None, is_group=False):
        sql_builder = SQLQueryBuilder(self.__sql_helper)
        sql_builder.visit(child, context=context)

        self.__vars.update(sql_builder.vars)

        combine_where = self.__combine_where(op, sql_builder)

        for bucket, wheres in combine_where.items():
            op = None
            sql = ''
            for where in wheres:
                operator, expr = where
                if op is not None:
                    sql += op

                sql += expr
                op = operator

            if len(wheres) > 1 or is_group:
                sql = self.wrap_in_parentheses(sql)

            self.__where.setdefault(bucket, []).append((None, sql))

    def __visit_binary_operation(self, node, parents, context, op):
        context = context or {}
        context['op'] = op
        for child in node.children:
            self.visit(child, context=context)

    def visit_and_operation(self, node, parents, context):
        self.__visit_binary_operation(node, parents, context, 'AND')

    def visit_or_operation(self, node, parents, context):
        self.__visit_binary_operation(node, parents, context, 'OR')

    @classmethod
    def wrap_in_parentheses(cls, text):
        return '(%s)' % text

    def build_vars(self):
        if not self.__vars:
            return None

        return self.__vars

    def __build_where(self):
        sql = ''
        for bucket, wheres in sorted(self.__where.items()):
            last_operator = None

            for where in wheres:
                operator, expr = where

                if last_operator:
                    sql += last_operator
                elif sql:
                    sql += operator

                sql += expr

                last_operator = operator

        return sql

    def build_where(self):
        return self.__build_where() or None  # Make sure to return None and not empty string

    @property
    def where(self):
        return self.__where

    @property
    def vars(self):
        return self.__vars


def get_split_vars(split):
    sql_vars = {}

    start = 0.
    for phase, percentage in split:
        sql_vars['phase_%s_start' % phase] = start
        sql_vars['phase_%s_end' % phase] = start + percentage

        start += percentage

    return sql_vars


def parse_query(query):
    return parser().parse(query, lexer=lexer())


def tree_to_sql_parts(tree, sql_helper):
    sql_builder = SQLQueryBuilder(sql_helper)
    resolver = UnknownOperationResolver(OrOperation)
    sql_builder.visit(resolver(tree))

    return sql_builder.build_vars(), sql_builder.build_where()


if __name__ == '__main__':  # pragma: no cover
    parse_query('version:a196d73071e57874768e20267a1bec4ed0a8c2b7')
