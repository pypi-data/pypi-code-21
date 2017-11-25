from typing import Union, Callable, List

from faker import Faker


GeneratedValue = Union[str, int]


class UniqueGen:
    _fake = None

    _generated_unique_words = None
    _generated_unique_ints = None

    def __init__(self):
        self._fake = Faker()
        self._generated_unique_words = []
        self._generated_unique_ints = []

    def word(self) -> str:
        word = self._unique_value(
            generator_fn=self._fake.word,
            generated_values_list=self._generated_unique_words,
        )
        return word

    def integer(self) -> int:
        integer = self._unique_value(
            generator_fn=self._fake.pyint,
            generated_values_list=self._generated_unique_ints,
        )
        return integer

    def _unique_value(
        self,
        generator_fn: Callable[[], GeneratedValue],
        generated_values_list: List[GeneratedValue],
        attempts_limit: int = 400,
    ) -> GeneratedValue:
        attempts_count = 0
        while attempts_count < attempts_limit:
            attempts_count += 1

            generated_value = generator_fn()
            is_generated_unique = generated_value not in generated_values_list
            if is_generated_unique:
                generated_values_list.append(generated_value)
                return generated_value
        else:
            raise UniqueGenError(
                "Unable to generate any more unique words. Usually if Faker "
                "didn't generate a unique word after ~200 attempt - he won't."
            )


class UniqueGenError(Exception):
    pass
