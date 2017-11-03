from textwrap import dedent
import unittest
from lib2to3.refactor import RefactoringTool, get_fixers_from_package


class FixerTestBase(unittest.TestCase):
    def setUp(self):
        fixes = get_fixers_from_package('trollius_fixers')
        self.tool = RefactoringTool(fixes)

    def do(self, input, output):
        input = dedent(input)
        output = dedent(output)
        refactored = str(self.tool.refactor_string(input, 'dummy.py'))
        self.assertEqual(output, refactored)


class TestImports(FixerTestBase):
    def test_import(self):
        input = """
            import trollius
            trollius.get_event_loop()
            """
        output = """
            import asyncio
            asyncio.get_event_loop()
            """
        self.do(input, output)

    def test_from_import(self):
        input = """
            from trollius import (ensure_future, wait)
            from trollius import get_event_loop
            get_event_loop()
            """
        output = """
            from asyncio import (ensure_future, wait)
            from asyncio import get_event_loop
            get_event_loop()
            """
        self.do(input, output)

    def test_decorator(self):
        input = """
            import trollius
            @trollius.coroutine
            def coro():
                pass
        """
        output = """
            import asyncio
            @asyncio.coroutine
            def coro():
                pass
        """
        self.do(input, output)


class TestYieldFrom(FixerTestBase):
    def test_simple(self):
        input = """
            from trollius import From
            def coro():
                yield From(func())
            """
        output = """

            def coro():
                yield from(func())
            """
        self.do(input, output)

    def test_full_name(self):
        input = """
            import trollius
            def coro():
                yield trollius.From(func())
            """
        output = """
            import asyncio
            def coro():
                yield from(func())
            """
        self.do(input, output)

    def test_name_inside(self):
        input = """
            import trollius
            from trollius import From
            def coro(future):
                yield From(trollius.wait(future))
        """
        output = """
            import asyncio

            def coro(future):
                yield from(asyncio.wait(future))
        """
        self.do(input, output)


class TestRaiseReturn(FixerTestBase):
    def test_simple(self):
        input = """
            from trollius import Return
            def coro():
                raise Return(0)
        """
        output = """

            def coro():
                return (0)
        """
        self.do(input, output)

    def test_tuple(self):
        input = """
            from trollius import Return
            def coro():
                raise Return((1, 2))
        """
        output = """

            def coro():
                return (1, 2)
        """
        self.do(input, output)

    def test_full_name(self):
        input = """
            import trollius
            def coro():
                raise trollius.Return(1)
            """
        output = """
            import asyncio
            def coro():
                return (1)
            """
        self.do(input, output)

    def test_name_inside(self):
        input = """
            import trollius
            from trollius import From, Return
            def coro(future):
                raise Return((yield From(trollius.wait(future))))
        """
        output = """
            import asyncio

            def coro(future):
                return (yield from(asyncio.wait(future)))
        """
        self.do(input, output)


class TestImportFromReturn(FixerTestBase):
    def test_star(self):
        input = """
            from trollius import *
        """
        output = """
            from asyncio import *
        """
        self.do(input, output)

    def test_single(self):
        input = """
            from trollius import From
            from trollius import Return
            from trollius import ensure_future
        """
        output = """


            from asyncio import ensure_future
        """
        self.do(input, output)

    def test_multiple(self):
        input = """
            from trollius import From, Return
            from trollius import ensure_future, From, Return
            from trollius import From, Return, wait
            from trollius import (
                wait_for, From, ensure_future, Return, wait)
        """
        output = """

            from asyncio import ensure_future
            from asyncio import wait
            from asyncio import (
                wait_for, ensure_future, wait)
        """
        self.do(input, output)
