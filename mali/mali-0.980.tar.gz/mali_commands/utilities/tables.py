# coding=utf-8


def dict_to_csv(d, fields):
    total_keys = fields or sorted(d.keys())

    yield total_keys

    def get_row():
        for key in total_keys:
            yield obj.get(key, '')

    if isinstance(d, dict):
        d = [d]

    for obj in d:
        yield list(get_row())


def format_json_data(json_data, formatters=None):
    if formatters is None:
        return json_data

    for row in json_data:
        for field, formatter in formatters.items():
            if field in row:
                row[field] = formatter(row[field])

    return json_data
