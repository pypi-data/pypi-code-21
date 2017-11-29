import construct_pre_method_string

def _(methods, address, class_name):
    ret = construct_pre_method_string._(methods, address, class_name)

    string_methods = []
    for name, body in methods.items():
        string_method = ''
        if 'test' in class_name:
            string_method += "\n        [Test]\n        "
        string_method += '\n        '.join(body)
        string_methods.append(string_method)

    ret += '\n        ' + '\n\n        '.join(string_methods) + '\n    }\n}'
    return ret[1:]
