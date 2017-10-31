from enum import Enum


class AutoEnum(Enum):

    def __str__(self):
        return self.name

    def _generate_next_value_(name, start, count, last_values):
        return name

    @classmethod
    def listall(cls):
        return [
            name for name, member in cls.__members__.items()
        ]
