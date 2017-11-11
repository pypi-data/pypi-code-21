def parse(line):
    within_quotes = False
    sep_ndxs = []
    for i, char in enumerate(line):
        if char == '"':
            within_quotes = not within_quotes
        elif char == ',':
            if not within_quotes:
                sep_ndxs.append(i)

    flds = []
    flds.append(line[:sep_ndxs[0]])
    for i in range(1, len(sep_ndxs)):
        sep_ndx = sep_ndxs[i]
        last_sep_ndx = sep_ndxs[i-1] + 1
        flds.append(line[last_sep_ndx:sep_ndx])
    flds.append(line[sep_ndxs[-1]+1:])
    return flds
