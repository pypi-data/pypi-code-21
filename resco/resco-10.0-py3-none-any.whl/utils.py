import os


def touch(fname):
    open(fname, 'a').close()


def create_tree(tree, prefix=''):
    if isinstance(tree, str):
        touch(os.path.join(prefix, tree))
    elif isinstance(tree, (list, tuple)):
        for element in tree:
            create_tree(element, prefix=prefix)
    elif isinstance(tree, dict):
        for folder, content in tree.items():
            os.makedirs(os.path.join(prefix, folder), exist_ok=True)
            create_tree(content, prefix=os.path.join(prefix, folder))
    else:
        raise ValueError('Invalid tree specification')
