class ColumnAlignment(object):
    def __init__(self, value):
        self.value = value

    def has_flag(self, flag):
        if isinstance(flag, ColumnAlignment):
            return self.value & flag.value > 0
        elif isinstance(flag, int):
            return self.value & flag > 0
        return False

    def __eq__(self, other):
        if isinstance(other, ColumnAlignment):
            return self.value == other.value
        elif isinstance(other, int):
            return self.value == other
        return False


LEFT = ColumnAlignment(1)
RIGHT = ColumnAlignment(2)
CENTER = ColumnAlignment(3)
