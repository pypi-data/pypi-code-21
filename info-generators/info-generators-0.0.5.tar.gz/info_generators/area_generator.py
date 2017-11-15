import random

from gabc_generator import Generator
import os

class AreaGenerator(Generator):
    @staticmethod
    def get():
        codes_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'consts/codes.txt')
        cities_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'consts/city.txt')

        codes = open(codes_path, encoding='utf-8').readlines()
        cities = open(cities_path, encoding='utf-8').readlines()
        city = random.choice(cities)
        city = city.split(',')

        def get_code():
            for item in codes:
                code = item.split(',')[0]
                name = item.split(',')[1]

                if city[0].startswith(code):
                    return (code, name)
            return None

        code = get_code()

        return (city[0], '{}{}'.format(code[1], city[1]).strip())
