class Hexa32(object):
    def __init__(self):
        self.PLUS = 'x'
        self.MINUS = 'z'

    def toLong32(self, str):
        if not str or not len(str):
            return 0

        first_str = str[0]
        if first_str == self.MINUS:
            return -1 * int(str[1:], 32)
        elif first_str == self.PLUS:
            return int(str[1:], 32)
        else:
            return int(str)
