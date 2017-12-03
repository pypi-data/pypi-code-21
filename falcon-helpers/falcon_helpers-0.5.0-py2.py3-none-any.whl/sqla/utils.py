import datetime
import random

import sqlalchemy as sa


def random_data_for_type(column, numeric_low=-100, numeric_high=100):
    """Return random data based on the data type

    :param column: The SQLA Column to consider


    """
    def randstring(len):
        return "".join([random.choice(string.ascii_letters)
                        for _ in range(len)])

    if isinstance(column.type, sa.types.Enum):
        return random.choice(column.type.enums)
    elif isinstance(column.type, sa.types.Boolean):
        return random.choice([True, False])
    elif isinstance(column.type, sa.types.Integer):
        return random.randint(numeric_high, numeric_low)
    elif isinstance(column.type, sa.types.Numeric):
        return random.uniform(numeric_high, numeric_low)
    elif isinstance(column.type, sa.types.Date):
        return datetime.date.today()
    elif isinstance(column.type, sa.types.DateTime):
        return datetime.datetime.utcnow()
    elif isinstance(column.type, columns.Point):
        return (0, 0)
    elif isinstance(column.type, (sa.types.String, sa.types.Unicode)):
        return randstring(min(column.type.length or 25, 25))

    raise ValueError('No randomization for this column type')
