import random

from .area_generator import AreaGenerator
from .gabc_generator import Generator
from .name_generator import NameGenerator


class AddressGenerator(Generator):
    @staticmethod
    def get():
        return '{area} {road}路 {no}号 {block}小区 {party}单元 {house}室'.format(
            area=AreaGenerator.get()[1],
            road=NameGenerator.get_last_name(),
            no=random.randint(100, 2000),
            block=NameGenerator.get_last_name(),
            party=random.randint(1, 3),
            house=random.randint(100, 600)
        )
