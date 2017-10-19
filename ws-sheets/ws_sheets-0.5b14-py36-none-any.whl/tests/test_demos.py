import numpy
import unittest
import collections

import ws_sheets.tests.conf.simple

class TestBase(unittest.TestCase):
    def setUp(self):
        self.book = ws_sheets.Book(ws_sheets.tests.conf.simple.Settings)

    def setup(self, book):
        pass

    def test(self):
        self.setup(self.book)

    async def atest(self):
        self.setup(self.book)

    def _test_selenium(self, driver):
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By

        print('wait for page to load')
        WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, 
                    '/html/body')))
        
        e = driver.find_element_by_xpath('/html/body')

        print('body found')
        print(e)
        
        for e in driver.find_elements(By.XPATH, '/html/body/*'):
            print(e.tag_name, repr(e.text))


        WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, 
                    '//table[@class="htCore"]')))

class TestAddRowAndColumn(TestBase):
    def setup(self, b):
        print(b.__class__)
        print(b['0'].__class__)
        b['0'].add_column(None)
        b['0'].add_row(None)
        b['0'].add_column(0)
        b['0'].add_row(0)

class TestImport(TestBase):
    def setup(self, b):
        b.set_script_pre('import math\nprint(math)\n')
        b.set_cell('0', 0, 0, 'math.pi')

    def test(self):
        self.setup(self.book)
        print(self.book['0'][0, 0])

class TestNamedRange(TestBase):
    def setup(self, book):

        string_named_range = "def a():\n  return book['0'][0:2, 0]"
    
        book.set_script_pre(string_named_range)
    
        book.set_cell('0', 0, 0, '1')
        book.set_cell('0', 1, 0, '2')
        book.set_cell('0', 2, 0, 'a()')
    
    def test(self):
        self.setup(self.book)

        print(self.book['0'][2, 0])

    async def atest(self):
        self.setup(self.book)

        print(await self.book['0'].getitem((2, 0)))

class TestSum(TestBase):
    def setup(self, bp):
    
        bp.set_cell('0', 0, 0, '1')
        bp.set_cell('0', 1, 0, '2')
        bp.set_cell('0', 2, 0, '3')
        bp.set_cell('0', 3, 0, '4')
        bp.set_cell('0', 4, 0, '5')
    
        bp.set_cell('0', 0, 1, 'sum(sheet[0:5, 0])')
    
    def test(self):
        self.setup(self.book)
        
        assert self.book['0'][0, 1] == 15

class TestIndexof(TestBase):
    def setup(self, bp):
    
        bp.set_script_pre("import numpy\ndef indexof(arr, a):\n  i = numpy.argwhere(arr == a)\n  return i")
    
        bp.set_cell('0', 0, 0, '1')
        bp.set_cell('0', 1, 0, '2')
        bp.set_cell('0', 2, 0, '3')
        bp.set_cell('0', 3, 0, '4')
        bp.set_cell('0', 4, 0, '5')
    
        bp.set_cell('0', 0, 1, 'indexof(sheet[0:5, 0], 3)')

    def test(self):
        self.setup(self.book)

        print('test indexof', self.book['0'][0, 1])
    
class TestLookup(TestBase):

    def setup(self, b):
        b.set_docs("In the script, the statement ``in_ == value`` produces a array of booleans with size equal to ``in_`` which is true where values of ``in_`` are equal to ``value``. The ``numpy.argwhere`` functions returns an array of indicies where the input array is True. So we get a potentially shorter array with the indicies of ``in_`` that meet our criteria. We then index ``result`` using that array, which will return the values of ``result`` at those indices.")
    
        b.set_script_pre("import numpy\ndef lookup(a, b, c):\n  return c[numpy.argwhere(b == a)]")
    
        b.set_cell('0', 0, 0, "'Bob'")
        b.set_cell('0', 1, 0, "'Sue'")
        b.set_cell('0', 2, 0, "'Jim'")
        b.set_cell('0', 3, 0, "'Pat'")
        
        b.set_cell('0', 0, 1, "'apple'")
        b.set_cell('0', 1, 1, "'banana'")
        b.set_cell('0', 2, 1, "'pear'")
        b.set_cell('0', 3, 1, "'fig'")
    
        b.set_cell('0', 0, 2, """lookup('Sue', sheet[:, 0], sheet[:, 1])""")
    
    def test(self):
        self.setup(self.book)

        print('test lookup', self.book['0'][0, 2])

        self.assertEqual(
                numpy.array([['banana']]),
                self.book['0'][0, 2])

class TestDatetime(TestBase):
    def setup(self, b):
        b.set_script_pre("import datetime\nimport pytz")
    
        b.set_cell('0', 0, 0, "datetime.datetime.now()")
        b.set_cell('0', 0, 1, "sheet[0, 0].item().tzinfo")
        b.set_cell('0', 1, 0, "datetime.datetime.utcnow()")
        b.set_cell('0', 1, 1, "sheet[1, 0].item().tzinfo")
        b.set_cell('0', 2, 0, "datetime.datetime.now(pytz.utc)")
        b.set_cell('0', 2, 1, "sheet[2, 0].item().tzinfo")

    def test(self):
        self.setup(self.book)

        print('test datetime', self.book['0'][0, 0])
        print('test datetime', self.book['0'][0, 1])
        print('test datetime', self.book['0'][1, 0])
        print('test datetime', self.book['0'][1, 1])
        print('test datetime', self.book['0'][2, 0])
        print('test datetime', self.book['0'][2, 1])

class TestStrings(TestBase):
    def setup(self, b):
        b.set_docs("""
`python str documentation`_

.. _`python str documentation`: https://docs.python.org/3.6/library/stdtypes.html#text-sequence-type-str
""")

        b.set_script_pre("s = 'The quick brown fox jumps over the lazy dog'")

        b.set_cell('0', 0, 0, "s.lower()")
        b.set_cell('0', 1, 0, "s.upper()")
        b.set_cell('0', 2, 0, "s[16:19]")

    def test(self):
        self.setup(self.book)

        print('test strings', self.book['0'][0, 0])
        print('test strings', self.book['0'][1, 0])
        print('test strings', self.book['0'][2, 0])

class TestMath(TestBase):
    def setup(self, b):
        b.set_docs("""
`python standard library: math`__

.. _math: https://docs.python.org/3/library/math.html

__ math_
""")

        b.set_script_pre("""
import math
""")

        b.set_cell('0', 0, 0, "math.pi")
        b.set_cell('0', 1, 0, "math.sin(math.pi)")
        b.set_cell('0', 2, 0, "math.cos(math.pi)")
        b.set_cell('0', 3, 0, "math.sqrt(4)")
        b.set_cell('0', 4, 0, "math.pow(2, 2)")
        b.set_cell('0', 5, 0, "math.exp(1)")

class TestNumericalTypes(TestBase):
    def setup(self, b):
        b.set_docs("""
`python numerical types`__

.. _link: https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex

__ link_
""")

        b.set_script_pre("""
x = 3
y = 2
""")

        b.set_cell('0',  0, 0, "x + y")
        b.set_cell('0',  1, 0, "x - y")
        b.set_cell('0',  2, 0, "x / y")
        b.set_cell('0',  3, 0, "x // y")
        b.set_cell('0',  4, 0, "x % y")
        b.set_cell('0',  5, 0, "-x")
        b.set_cell('0',  6, 0, "+x")
        b.set_cell('0',  7, 0, "abs(x)")
        b.set_cell('0',  8, 0, "int(x)")
        b.set_cell('0',  9, 0, "float(x)")
        b.set_cell('0', 10, 0, "complex(x, y)")
        b.set_cell('0', 11, 0, "complex(x, y).conjugate()")
        b.set_cell('0', 12, 0, "divmod(x, y)")
        b.set_cell('0', 13, 0, "pow(x, y)")
        b.set_cell('0', 14, 0, "x ** y")
    
    def test(self):
        self.setup(self.book)
 
class TestLookup2(TestBase):
    def setup(self, b):
        b.set_docs("In the script, the statement ``in_ == value`` produces a array of booleans with size equal to ``in_`` which is true where values of ``in_`` are equal to ``value``. The ``numpy.argwhere`` functions returns an array of indicies where the input array is True. So we get a potentially shorter array with the indicies of ``in_`` that meet our criteria. We then index ``result`` using that array, which will return the values of ``result`` at those indices.")

        b.set_script_pre("""
import numpy
import operator

def lookup(value, in_, result):
    return result[numpy.argwhere(in_ == value)]

def lookup_ifs(result, *args):
    b = numpy.broadcast_to(True, numpy.shape(result))
    for in_, value, op in args:
        b = numpy.logical_and(b, in_ == value)
    return result[numpy.argwhere(b)]
""")
    
        b.set_cell('0', 0, 0, '1')
        b.set_cell('0', 1, 0, '2')
        b.set_cell('0', 2, 0, '3')
        b.set_cell('0', 3, 0, '4')
        b.set_cell('0', 4, 0, '5')
        b.set_cell('0', 5, 0, '6')
        
        b.set_cell('0', 0, 1, '1')
        b.set_cell('0', 1, 1, '2')
        b.set_cell('0', 2, 1, '3')
        b.set_cell('0', 3, 1, '4')
        b.set_cell('0', 4, 1, '5')
        b.set_cell('0', 5, 1, '6')
 
        b.set_cell('0', 0, 2, "'a'")
        b.set_cell('0', 1, 2, "'b'")
        b.set_cell('0', 2, 2, "'c'")
        b.set_cell('0', 3, 2, "'d'")
        b.set_cell('0', 4, 2, "'e'")
        b.set_cell('0', 5, 2, "'f'")

       
        b.set_cell('0', 0, 3, 'lookup_ifs(sheet[:,2], (sheet[:,0], 2, operator.gt), (sheet[:,1], 5, operator.lt))')
    
    def test(self):
        self.setup(self.book)
        b = self.book

        print(b.script_pre.output)

        assert numpy.all(self.book['0'][0, 3] == numpy.array(['c','d']))
       
DEMOS = collections.OrderedDict((
            ('add_row_and_column', TestAddRowAndColumn),
            ('named_range', TestNamedRange),
            ('import', TestImport),
            ('sum', TestSum),
            ('indexof', TestIndexof),
            ('lookup', TestLookup),
            ('lookup2', TestLookup2),
            ('datetime', TestDatetime),
            ('string', TestStrings),
            ('math', TestMath),
            ('numericaltypes', TestNumericalTypes),
            ))





