import os

def _(src, path, namespace_depth):
    for name, namespace in src['namespaces'].items():
        if namespace_depth == 0:
            _(namespace, path + os.sep + name, 0)
        else:
            _(namespace, path, namespace_depth - 1)

    for name, body in src['classes'].items():
        if not os.path.exists(path):
            os.makedirs(path)

        with open(path + os.sep + name + '.cs', 'w') as f:
            f.write(body)
