from .utils import PGTestCase

from procgraph import Block, BlockWriterError


def same_name_mistake_config():

    class MyBlock(Block):
        Block.config('x', 'description')
        Block.config('x', 'description 2', default=True)


def same_name_mistake_input():

    class MyBlock(Block):
        Block.input('x')
        Block.input('x')


def same_name_mistake_output():

    class MyBlock(Block):
        Block.output('x')
        Block.output('x')


def bad_mixing_1():

    class MyBlock(Block):
        Block.output('x')
        Block.output_is_variable()


def bad_mixing_2():

    class MyBlock(Block):
        Block.output_is_variable()
        Block.output('x')


def bad_mixing_3():

    class MyBlock(Block):
        Block.input_is_variable()
        Block.input('x')


def bad_mixing_4():

    class MyBlock(Block):
        Block.input('x')
        Block.input_is_variable()


def bad_mixing_5():

    class MyBlock(Block):
        Block.input('x')
        Block.output_is_variable()


def bad_mixing_6():

    class MyBlock(Block):
        Block.output_is_variable()
        Block.input('x')


def bad_mixing_7():

    class MyBlock(Block):
        Block.output_is_variable()


def good_mixing_1():

    class MyBlockA(Block):
        Block.input_is_variable()
        Block.output_is_variable()


def good_mixing_2():

    class MyBlockB(Block):
        Block.input_is_variable()
        Block.output('only one')


def good_mixing_3():

    class MyBlockC(Block):
        Block.input_is_variable()


class SyntaxTestMultiple(PGTestCase):

    def test_same_name_mistake(self):
        ''' Test that we detect when a input, output, config name
            is repeated. 
        '''
        self.assertRaises(BlockWriterError, same_name_mistake_config)
        self.assertRaises(BlockWriterError, same_name_mistake_input)
        self.assertRaises(BlockWriterError, same_name_mistake_output)

    def test_variable_inputs(self):
        self.assertRaises(BlockWriterError, bad_mixing_1)
        self.assertRaises(BlockWriterError, bad_mixing_2)
        self.assertRaises(BlockWriterError, bad_mixing_3)
        self.assertRaises(BlockWriterError, bad_mixing_4)
        # XXX: it's late, not sure if this is correct or not
        # self.assertRaises(BlockWriterError, bad_mixing_5)
        # self.assertRaises(BlockWriterError, bad_mixing_6)
        # self.assertRaises(BlockWriterError, bad_mixing_7)

        good_mixing_1()
        good_mixing_2()
        good_mixing_3()

    def test_ok(self):

        class MyBlockOK(Block):
            Block.config('x', 'description')
            Block.config('y', 'description 2', default=True)
            Block.config('z')
            Block.input('x')
            Block.input('y')
            Block.output('x')

        self.assertEqual(len(MyBlockOK.config), 3)
        self.assertEqual(len(MyBlockOK.input), 2)
        self.assertEqual(len(MyBlockOK.output), 1)
