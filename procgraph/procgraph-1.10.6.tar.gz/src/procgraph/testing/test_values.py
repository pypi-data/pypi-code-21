from .utils import PGTestCase

from ..core.parsing import parse_value
from ..core.parsing_elements import VariableReference

examples = {
            '0': 0,
            '0.0': 0.0,
            '1.0': 1.0,
            '1': 1,
            '[]': [],
            '[1]': [1],
            '[1.0]': [1.0],
            '[1,2]': [1, 2],
            '[1,[2]]': [1, [2]],
            '[[]]': [[]],
            '[{}]': [{}],
            '{}': {},
            '[{a:0}]': [{'a':0}],
            # XXX 
            #'{a:[]}': {"a":[]},
            '{a:0}': {'a': 0},
            '{a:0,b:1}': {'a': 0, 'b': 1},
            '{a:b}': {'a': 'b'},
            '{a:{b:c}}': {'a': {'b': 'c'}},

        """{ indices: [0,170] }""": {'indices': [0, 170]},

        """{ indices: [0,170], theta: [-1,+1], color: 'r', \
            origin: [0,0,0],  max_readings: 5}""":
{'indices': [0, 170], 'theta': [-1, +1], 'color': 'r',
      'origin': [0, 0, 0], 'max_readings': 5},

"""[{ indices: [0,170], theta: [-1,+1], color: 'r', \
      origin: [0,0,0],  max_readings: 5}, { indices: [171,341], \
        theta: [+1,+5], color: 'b', origin: [0,0,0], max_readings: 5}]""":
[{'indices': [0, 170], 'theta': [-1, +1], 'color': 'r',
      'origin': [0, 0, 0], 'max_readings': 5},
{'indices': [171, 341],
        'theta': [+1, +5], 'color': 'b', 'origin': [0, 0, 0],
        'max_readings': 5}],

        '...': Ellipsis,
        '[1,2,...]': [1, 2, Ellipsis],

        '$v': VariableReference('v'),

        # simple string is a string
        'goodname': 'goodname'
}


class SyntaxTest2(PGTestCase):

    def test_numbers(self):
        self.assertEqual(type(parse_value('1')), int)

    def test_numbers2(self):
        self.assertEqual(type(parse_value('1.0')), float)
        #assert isinstance(parse_value('1.0'), float)

    def test_numbers3(self):
        l = parse_value('[1.0]')
        assert isinstance(l[0], float)

    def test_numbers4(self):
        l = parse_value('[1]')
        assert isinstance(l[0], int)

    def testExamples(self):
        for example, expected in examples.items():
            print("Trying '%s'" % example)
            found = parse_value(example)

            ok = (found == expected) or (str(found) == str(expected))

            if not ok:
                msg = 'Parsing: %r\n' % example
                msg += ' expected: %r (%s) \n' % (expected, type(expected))
                msg += '    found: %r (%s) \n' % (found, type(found))
                raise Exception(msg)


