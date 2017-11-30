from typing import Callable

from shuup_testutils.generators.unique import UniqueGen
from shuup_testutils.generators.unique import GeneratedValue
from shuup_testutils.generators.unique import UniqueGenError
from shuup_testutils.cases import SnakeTestCase


class UniqueGenTest(SnakeTestCase):
    unique_gen = None

    def set_up(self):
        super().set_up()
        self.unique_gen = UniqueGen()

    def test_unique_word_generator_limit(self):
        with self.assert_raises(UniqueGenError):
            for _ in range(0, 500):
                self.unique_gen.word()

    def test_unique_word_uniqueness(self):
        self._test_uniqueness(generator_fn=self.unique_gen.word)

    def test_unique_int_uniqueness(self):
        self._test_uniqueness(generator_fn=self.unique_gen.integer)

    def _test_uniqueness(
        self,
        generator_fn: Callable[[], GeneratedValue],
        values_amount: int = 150,
    ):
        values_generated = []
        for _ in range(0, values_amount):
            value_generated = generator_fn()
            self.assert_true(value_generated not in values_generated)
            values_generated.append(value_generated)
