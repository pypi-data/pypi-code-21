"""Autogenerate converter between some formats.

"""
from rofetta.utils import output_as_tempfile
from . import routines


def converter(informat:str, outformat:str) -> callable:
    """Return a function that convert given informat to given outformat"""
    reader = getattr(routines, 'read_' + informat, None)
    writer = getattr(routines, 'write_' + outformat, None)
    if reader and writer:
        def make_converter(reader, writer):
            @output_as_tempfile
            def converter_func(fin:str, fout:str=None, *, reader=reader, writer=writer):
                with open(fin) as ifd, open(fout, 'w') as ofd:
                    for line in writer(reader(iter(ifd))):
                        ofd.write(line)
            return converter_func

        return make_converter(reader, writer)
    raise ValueError("No converter exist between {} and {}".format(informat, outformat))


convert_slf_to_cxt = converter('slf', 'cxt')
convert_cxt_to_slf = converter('cxt', 'slf')
