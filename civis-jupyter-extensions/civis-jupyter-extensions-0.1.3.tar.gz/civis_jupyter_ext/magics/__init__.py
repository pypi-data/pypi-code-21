from . import query

_MAGICS = [query]


def load_ipython_extension(ipython):
    """Load ipython magics.

    To add a new magic, create one in a a module (see query.py for an
    example). Then add it to the list above.
    """

    for module in _MAGICS:
        ipython.register_magic_function(
            getattr(module, 'magic'),
            magic_kind='line_cell',
            magic_name=getattr(module, 'MAGIC_NAME'))
