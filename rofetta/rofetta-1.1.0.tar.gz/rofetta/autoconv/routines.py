"""Readers and writers for various formats.

They will be plugged together by autoconv module

"""


SLF_HEADERS = {'lattice', 'objects', 'attributes', 'relation'}


def read_cxt(lines:iter):
    """Yield, in that order:

    - number of objects
    - number of attributes
    - tuple of objects
    - tuple of attributes
    - for each object:
        - (object, bools)

    """
    assert next(lines) == 'B\n', 'expects a B'
    assert next(lines) == '\n', 'expects empty line'
    nb_obj, nb_att = map(int, (next(lines), next(lines)))
    yield nb_obj
    yield nb_att
    assert next(lines) == '\n', 'expects empty line'
    objects = tuple(next(lines).strip() for _ in range(nb_obj))
    attributes = tuple(next(lines).strip() for _ in range(nb_att))
    yield objects
    yield attributes
    for properties in lines:
        yield tuple(char.lower() == 'x' for char in properties)


def write_cxt(reader:callable) -> iter:
    """Yield cxt lines knowing that reader will return, in that order:

    - number of objects
    - number of attributes
    - tuple of objects
    - tuple of attributes
    - for each object:
        - booleans relations

    """
    yield 'B\n\n'
    nb_obj, nb_att = next(reader), next(reader)
    yield str(nb_obj) + '\n'
    yield str(nb_att) + '\n\n'
    for object in next(reader):
        yield str(object) + '\n'
    for attribute in next(reader):
        yield str(attribute) + '\n'
    for props in reader:
        yield ''.join('X' if hold else '.' for hold in props) + '\n'


def read_slf(lines:str):
    """Yield, in that order:

    - number of objects
    - number of attributes
    - tuple of objects
    - tuple of attributes
    - for each object:
        - (object, bools)

    """
    for line in lines:
        if line.startswith('['):
            header = line.strip('[]\n').lower()
            assert header in SLF_HEADERS, header
            if header == 'lattice':
                nb_obj, nb_att = map(int, (next(lines), next(lines)))
                yield nb_obj
                yield nb_att
            elif header == 'objects':
                objects = tuple(next(lines).strip() for _ in range(nb_obj))
                yield objects
            elif header == 'attributes':
                attributes = tuple(next(lines).strip() for _ in range(nb_att))
                yield attributes
            elif header == 'relation':
                for line in lines:
                    yield tuple(bool(int(attr)) for attr in line.strip().split())
            else:
                raise ValueError("Header {} is not handled".format(header))


def write_slf(reader:callable) -> iter:
    """Yield slf lines knowing that reader will return, in that order:

    - number of objects
    - number of attributes
    - tuple of objects
    - tuple of attributes
    - for each object:
        - booleans relations

    """
    nb_obj, nb_att = next(reader), next(reader)
    yield '[Lattice]\n'
    yield str(nb_obj) + '\n'
    yield str(nb_att) + '\n'
    yield '[Objects]\n'
    for object in next(reader):
        yield str(object) + '\n'
    yield '[Attributes]\n'
    for attribute in next(reader):
        yield str(attribute) + '\n'
    yield '[relation]\n'
    for props in reader:
        yield ' '.join('1' if hold else '0' for hold in props) + ' \n'
