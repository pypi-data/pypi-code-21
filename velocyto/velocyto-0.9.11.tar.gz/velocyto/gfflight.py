def feature_from_line(line, dialect=None, strict=True, keep_order=False):
    """
    Given a line from a GFF file, return a Feature object

    Parameters
    ----------
    line : string

    strict : bool
        If True (default), assume `line` is a single, tab-delimited string that
        has at least 9 fields.

        If False, then the input can have a more flexible format, useful for
        creating single ad hoc features or for writing tests.  In this case,
        `line` can be a multi-line string (as long as it has a single non-empty
        line), and, as long as there are only 9 fields (standard GFF/GTF), then
        it's OK to use spaces instead of tabs to separate fields in `line`.
        But if >9 fields are to be used, then tabs must be used.

    keep_order, dialect
        Passed directly to :class:`Feature`; see docstring for that class for
        description

    Returns
    -------
    A new :class:`Feature` object.
    """
    if not strict:
        lines = line.splitlines(False)
        _lines = []
        for i in lines:
            i = i.strip()
            if len(i) > 0:
                _lines.append(i)

        assert len(_lines) == 1, _lines
        line = _lines[0]

        if '\t' in line:
            fields = line.rstrip('\n\r').split('\t')
        else:
            fields = line.rstrip('\n\r').split(None, 8)
    else:
        fields = line.rstrip('\n\r').split('\t')
    try:
        attr_string = fields[8]
    except IndexError:
        attr_string = ""
    attrs, _dialect = parser._split_keyvals(attr_string, dialect=dialect)
    d = dict(list(zip(constants._gffkeys, fields)))
    d['attributes'] = attrs
    d['extra'] = fields[9:]
    d['keep_order'] = keep_order
    if dialect is None:
        dialect = _dialect
    return Feature(dialect=dialect, **d)
