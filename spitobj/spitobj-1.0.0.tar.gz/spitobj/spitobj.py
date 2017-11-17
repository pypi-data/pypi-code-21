import decimal
import random
import string
import sys
from collections import OrderedDict
from uuid import uuid4

import typing


class Spitobj:
    obj_class = typing.Callable
    obj = None
    fields = []

    def __init__(self, *args, **kwargs):
        for field, generator in self.fields:
            spitobj_class = getattr(generator, 'spitobj_class', None)
            if (isinstance(spitobj_class, str) and spitobj_class.lower() == 'self'):
                #TODO: handle possibly recursion
                print('possible recurrsion!!')
                generator.spitobj_class = type(self)
        self.generators = OrderedDict(self.fields)

    def new(self, *args, **kwargs):
        kwargs = kwargs or {}
        obj_data = {}
        for field_name, field_value in self.fields:
            if field_name in kwargs:
                continue
            if not isinstance(field_value, Generator):
                # branch for literals, like: 5, Decimal(10), "some-text"
                value = field_value
            else:
                # branch for generators, StringGenerator, CountedTextGenerator
                value = next(field_value)
            obj_data[field_name] = value
        obj_data.update(kwargs)
        try:
            obj = self.obj_class(**obj_data)
        except TypeError as err:
            msg = "Ensure {}.__init__ takes parameter {}".format(
                self.obj_class, err.args[0].split()[-1]
            )
            raise TypeError(msg) from err
        self.post_generation(obj, obj_data)
        self.obj = obj
        return obj

    def post_generation(self, obj, init_data):
        pass

    def get(self, *args, **kwargs):
        return self.new(*args, **kwargs)


class Generator:
    def __iter__(self):
        return self


class StringGenerator(Generator):
    def __init__(self, length=32, alphabet=string.ascii_letters):
        self.length = length
        self.alphabet = alphabet

    def __next__(self):
        while True:
            value = ''.join(
                random.choice(self.alphabet) for _ in range(self.length)
            )
            return value


class CounterGenerator(Generator):
    def __init__(self, start=0):
        self.start = start - 1

    def __next__(self):
        while True:
            self.start = self.start + 1
            return self.start


class DecimalGenerator(Generator):
    def __init__(self, low, high=None, precision=2):
        if high:
            self.low = low
            self.high = high
        else:
            self.low = 0
            self.high = low
        self.precision = precision
        self.low_with_prec = self.low * 10 ** self.precision
        self.high_with_prec = self.high * 10 ** self.precision

    def __next__(self):
        value = decimal.Decimal(
            random.randrange(self.low_with_prec, self.high_with_prec)
        )
        value /= 10 ** self.precision
        return value


#TODO: add spaces for it
global_counter = CounterGenerator()
class CountedTextGenerator(Generator):
    counter = global_counter

    def __init__(self, text, counter=None):
        assert 'idx' in text
        self.text = text
        if counter:
            self.counter = counter

    def __next__(self):
        while True:
            idx = next(self.counter)
            value = self.text.format(idx=idx)
            return value


class ObjectGenerator(Generator):
    def __init__(self, spitobj_class, *args, **kwargs):
        msg = "spitobj_class {!r} should subclass Spitobj".format(
            spitobj_class
        )
        if spitobj_class != 'Self':
            assert issubclass(spitobj_class, Spitobj), msg
        self.spitobj_class = spitobj_class
        self.spitobj_data = kwargs

    def __next__(self):
        spitobj = self.spitobj_class()
        while True:
            return spitobj.get(**self.spitobj_data)
