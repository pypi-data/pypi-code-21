from pyparsing import ParserElement
from procgraph.core.parsing_elements import parse_input_port, parse_output_port
# Enable memoization; much faster, but we can't use
# parse actions with side effects.
ParserElement.enablePackrat()

from pyparsing import (Regex, Word, delimitedList, alphas, Optional, OneOrMore,
    stringEnd, alphanums, ZeroOrMore, Group, Suppress, lineEnd,
    Combine, nums, Literal, CaselessLiteral,
    restOfLine, QuotedString, ParseException, Forward)

from .parsing_elements import (VariableReference, ParsedBlock,
    ParsedAssignment, ImportStatement, ParsedModel, ParsedSignal,
    ParsedSignalList, Connection, Where,
    output_from_tokens, input_from_tokens, config_from_tokens)
from .exceptions import PGSyntaxError


def eval_dictionary(s, loc, tokens): #@UnusedVariable
    if not 'content' in tokens:
        return {}
    d = {}
    for a in tokens:
        if 'value' in a:
            d[a['key']] = a['value']
    return d


def eval_array(s, loc, tokens): #@UnusedVariable
    elements = tokens.asList()
    res = []
    for i in range(len(elements)):
        t = elements[i]
        res.append(t)
    return res

# Shortcuts
S = Suppress
O = Optional

# Important: should be at the beginning
# make end of lines count
ParserElement.setDefaultWhitespaceChars(" \t")

# These are just values
# Definition of numbers
number = Word(nums)
point = Literal('.')
e = CaselessLiteral('E')
plusorminus = Literal('+') | Literal('-')
integer = Combine(O(plusorminus) + number)
# Note that '42' is not a valid float...
floatnumber = (Combine(integer + point + O(number) + O(e + integer)) |
                Combine(integer + e + integer))

ellipsis_value = Literal('...').setParseAction(lambda _: Ellipsis)


def convert_int(tokens):
    assert(len(tokens) == 1)
    return int(tokens[0])

integer.setParseAction(convert_int)
floatnumber.setParseAction(lambda tokens: float(tokens[0]))

# comments
comment = S(Literal('#') + restOfLine)
good_name = Combine(Word(alphas) + O(Word(alphanums + '_')))

# All kinds of python strings

single_quoted = (QuotedString('"', '\\', unquoteResults=True) |
                 QuotedString("'", '\\', unquoteResults=True))
multi_quoted = (QuotedString(quoteChar='"""', escChar='\\',
                              multiline=True, unquoteResults=True) |
                 QuotedString(quoteChar="'''", escChar='\\',
                              multiline=True, unquoteResults=True))
quoted = multi_quoted | single_quoted

reference = Combine(S('$') + good_name('variable'))

reference.setParseAction(VariableReference.from_tokens)

dictionary = Forward()
array = Forward()

value = (
          ellipsis_value |
          quoted |
          array |
          dictionary |
          reference |
          good_name | # order is important... 
          floatnumber |
          integer
         )('val')

# dictionaries

dict_key = good_name | quoted
dictionary << (S("{") +
    O(
             delimitedList(
                 Group(dict_key('key') + S(':') + value('value'))
                 )
             )('content') +
    S("}"))


dictionary.setParseAction(eval_dictionary)

array << Group(S("[") + O(delimitedList(value)('elements')) + S("]"))

array.setParseAction(eval_array)


def parse_value(string, filename=None):
    ''' This is useful for debugging '''

    try:
        ret_value = value.parseString(string, parseAll=True)
        return ret_value['val']

    except ParseException as e:
        where = Where(filename, string, line=e.lineno, column=e.col)
        raise PGSyntaxError('Error in parsing string: %s' % e, where=where)


def create_model_grammar():

    # We pass a "where" object to the constructors
    def wrap(constructor):
        def from_tokens(string, location, tokens):
            element = constructor(tokens)
            element.where = Where(ParsedModel.static_filename,
                                  string, location)
            return element
        return from_tokens

    arrow = S(Regex(r'-+>'))
    newline = S(lineEnd)

    # (don't put '.' at the beginning)
    qualified_name = Combine(good_name + '.' + (integer | good_name))

    block_name = good_name
    block_type = good_name | Word('_+-/*') | quoted | reference

    signal = (O(S('[') +
                (integer | good_name)('local_input') +
                S(']')) +
              O(block_name('block_name') + S(".")) +
              (integer | good_name)('name') +
             O(S('[') + (integer | good_name)('local_output') + S(']')))
    signal.setParseAction(wrap(ParsedSignal.from_tokens))

    signals = delimitedList(signal)
    signals.setParseAction(wrap(ParsedSignalList.from_tokens))

    # Note that here the order matters (as qualified = good + something)
    key = qualified_name | good_name

    key_value_pair = Group(key("key") + S('=') + value("value"))

    parameter_list = OneOrMore(key_value_pair)
    parameter_list.setParseAction(
        lambda s, l, t: dict([(a[0], a[1]) for a in t])) #@UnusedVariable

    block = (S("|") +
             O(block_name("name") + S(":")) +
             block_type("blocktype") +
             O(parameter_list("config")) +
             S("|"))
    block.setParseAction(wrap(ParsedBlock.from_tokens))

    input_port = S("(") + block_name("port_name") + S(")")
    output_port = S("(") + block_name("port_name") + S(")")
    output_port.setParseAction(wrap(parse_output_port))
    input_port.setParseAction(wrap(parse_input_port))


    between1 = arrow + O(signals + arrow)
    between2 = arrow + S(newline + arrow) + O(signals + arrow)
    between3 = newline + arrow + O(signals + arrow)
    between = between3 | between2 | between1

    # Different patterns
    arrow_arrow = (signals +
                   arrow +
                   O(block + ZeroOrMore(between + block)) +
                   arrow +
                   signals)
    source = (input_port | block) + ZeroOrMore(between + block) + arrow + signals
    sink = signals + arrow + ZeroOrMore(block + between) + (block | output_port)
    source_sink = block + ZeroOrMore(between + block)
    source_sink2 = input_port + ZeroOrMore(between + block)
    # |a| -> (out)
    source_sink3 = ZeroOrMore(block + between) + output_port
    # (in) -> |a| -> (out)
    source_sink4 = input_port + between + ZeroOrMore(block + between) + output_port

    # all of those are called a "connection"
    connection = arrow_arrow ^ sink ^ source ^ source_sink ^ source_sink2 ^ source_sink3 ^ source_sink4

    connection.setParseAction(wrap(Connection.from_tokens))

    # allow breaking lines with backslash
    continuation = '\\' + lineEnd
    connection.ignore(continuation)

    assignment = (key("key") + S('=') + value("value"))
    assignment.setParseAction(wrap(ParsedAssignment.from_tokens))

    package_name = good_name + ZeroOrMore('.' + good_name)
    import_statement = S('import') + package_name('package')
    import_statement.setParseAction(wrap(ImportStatement.from_tokens))

    config = (S('config') +
               good_name('variable') +
               O(S('=') + value('default')) +
               O(quoted('docstring')))
    config.setParseAction(wrap(config_from_tokens))

    input_s = S('input') + good_name('name') + O(quoted('docstring'))
    input_s.setParseAction(wrap(input_from_tokens))

    output = S('output') + good_name('name') + O(quoted('docstring'))
    output.setParseAction(wrap(output_from_tokens))



    docs = S(ZeroOrMore(multi_quoted + OneOrMore(newline)))

    action = (comment |
              config |
              input_s |
              output |
              (docs + connection) |
              (docs + assignment) |
              (docs + import_statement))

    model_content = (ZeroOrMore(newline) + action +
                    ZeroOrMore(OneOrMore(newline) + action) +
                    ZeroOrMore(newline))

    named_model = (
        S(Combine('---' + O(Word('-')))) + S('model') +
        good_name('model_name') + OneOrMore(newline) +
        O(quoted('docstring')) +
        model_content('content')
        )

    named_model.setParseAction(wrap(ParsedModel.from_named_model))

    anonymous_model = model_content.copy()
    anonymous_model.setParseAction(wrap(ParsedModel.from_anonymous_model))

    comments = ZeroOrMore((comment + newline) | newline)
    pg_file = (comments +
               (OneOrMore(named_model) | anonymous_model) +
               stringEnd) # important

    return pg_file

pg_file = create_model_grammar()


def parse_model(string, filename=None):
    ''' Returns a list of ParsedModel '''
    # make this check a special case, otherwise it's hard to debug
    if not string.strip():
        msg = 'Passed empty string.'
        raise PGSyntaxError(msg, Where(filename, string, 0))

    # this is not threadsafe (but we don't have threads, so it's all good)
    ParsedModel.static_filename = filename

    try:
        parsed = pg_file.parseString(string)
        return list(parsed)
    except ParseException as e:
        where = Where(filename, string, line=e.lineno, column=e.col)
        msg = 'Error in parsing string: %s' % e
        raise PGSyntaxError(msg, where=where)


# Register handler for ellipsis, so that ParsedModel is pickable.
# Ellipsis is they only object we use that is not pickable by default.
import copy_reg
import types


def code_unpickler(data): #@UnusedVariable
    return Ellipsis


def code_pickler(code): #@UnusedVariable
    return code_unpickler, (None,)

copy_reg.pickle(types.EllipsisType, code_pickler, code_unpickler)


