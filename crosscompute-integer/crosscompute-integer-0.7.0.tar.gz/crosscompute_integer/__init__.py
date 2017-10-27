from crosscompute.types import DataType, DataTypeError


class IntegerType(DataType):
    suffixes = 'integer', 'int', 'count'
    formats = 'txt',
    template = 'crosscompute_integer:type.jinja2'
    requires_value_for_path = False

    @classmethod
    def save(Class, path, integer):
        open(path, 'w').write(str(integer))

    @classmethod
    def parse(Class, x, default_value=None):
        try:
            integer = int(x)
        except (TypeError, ValueError):
            raise DataTypeError('expected integer')
        return integer

    @classmethod
    def render(Class, integer):
        return '%d' % integer
