import os

from folstools import googleapi

ROW_OFFSET = 2


def content_info(content):
    it = iter(content)
    first_line = next(it)
    next(it)
    return first_line, it


def content_indices(items, *args):
    return [items.index(key) for key in args]


def generate_localization_strings(doc_name, sheet, langs,
                                  specified_category=None):
    values = iter(googleapi.generate_spreadsheet(doc_name, sheet))
    first_line, it = content_info(values)
    indices = [first_line.index(key) for key in ['Category', 'English'] +
               list(langs.values())]
    indices = content_indices(first_line, 'Category', 'English',
                              *langs.values())

    trans = {}
    for items in it:
        try:
            category = items[indices[0]]
            english = items[indices[1]].strip()
            if specified_category and category != specified_category:
                continue
            tt = {}
            for i, lang in enumerate(langs.keys()):
                tt[lang] = items[indices[i + 2]].strip()
            trans[english] = tt
        except IndexError:
            pass
    return langs.keys(), trans
