
GRID_KWARGS = (u'row',
               u'column',
               u'columnspan',
               u'rowspan',
               u'sticky',
               u'padx',
               u'pady')


def pop_mandatory_kwarg(kwargs,
                        key):
    try:
        return kwargs.pop(key)
    except KeyError:
        raise ValueError(u'Missing mandatory parameter "{key}"'.format(key=key))


def pop_kwarg(kwargs,
              key,
              default=None):
    try:
        return kwargs.pop(key)
    except KeyError:
        return default


def raise_on_positional_args(caller, args):
    if args:
        raise ValueError(u'positional arguments are not accepted by {c}'.format(c=caller.__class__))


def kwargs_only(f):
    def new_f(**kwargs):
        return f(**kwargs)
    return new_f


def get_grid_kwargs(frame=None,
                    **kwargs):

    grid_kwargs = {key: value
                   for key, value in kwargs.iteritems()
                   if key in GRID_KWARGS}

    default_row = 0 if frame is None else frame.row.current
    default_column = 0 if frame is None else frame.column.current

    # Don't need to set row or column if it it's the current value
    grid_kwargs[u'row'] = grid_kwargs.get(u'row', default_row)
    grid_kwargs[u'column'] = grid_kwargs.get(u'column', default_column)

    return grid_kwargs


def get_widget_kwargs(**kwargs):
        return {key: value
                for key, value in kwargs.iteritems()
                if key not in GRID_KWARGS}
