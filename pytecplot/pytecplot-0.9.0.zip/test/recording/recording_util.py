from tecplot import tecutil


def translate(macro):
    return tecutil._tecutil_connector.translate_macro_to_python(macro)


def translate_with_raw_data(macro):
    return tecutil._tecutil_connector.translate_macro_with_raw_data_to_python(
        macro)


def IMPLICATION(p, q):
    return not p or q