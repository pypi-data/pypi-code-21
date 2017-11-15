from gabc_generator import Generator
import random

MOBILE_PREFIX = (133, 153, 177, 180,
                 181, 189, 134, 135, 136, 137, 138, 139, 150, 151, 152, 157, 158, 159,
                 178, 182, 183, 184, 187, 188, 130, 131, 132, 155, 156, 176, 185, 186,
                 145, 147, 170)


class MobileGenerator(Generator):
    @staticmethod
    def get():
        return '{}{}'.format(random.choice(MOBILE_PREFIX), random.randrange(11111111, 99999999))
