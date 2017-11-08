def get_item_path(bf, item):
    if hasattr(item, 'parent'):
        parent = bf.get(item.parent)
        return get_item_path(bf, parent) + [item]
    else:
        return [item]

def make_tree(path):
    if len(path)==1:
        value = path[0]
    else:
        value = make_tree(path[1:])
    return {path[0].id: value}

def merge(a, b, path=None):
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass # same leaf value
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a

def print_tree(tree, objects, indent=0):
    for key, value in tree.iteritems():
        is_dict = isinstance(value, dict)
        char = '-' if is_dict else '*'
        print ' '*indent+char, objects[key]
        if is_dict:
            print_tree(value, objects, indent=indent+2)

def print_path_tree(bf, results):
    paths = [get_item_path(bf, r) for r in results]
    path_objects = {o.id:o for p in paths for o in p}
    trees = [make_tree(path) for path in paths]
    print_tree(reduce(merge, trees), path_objects)

def print_collaborator_edit_resp(resp):
    for key, value in resp.iteritems():
        if value['success']:
            print " - {}: Success".format(key)
        else:
            print " - {}: Error - {}".format(key, value['message'])

def recursively_upload(bf,dest,files):
    import os
    from blackfynn import Collection
    
    dirs = [f for f in files if os.path.isdir(f)]
    files = [f for f in files if os.path.isfile(f)]
    if not dest.startswith('N:'):
        # maybe destination is dataset name?
        dest = bf.get_dataset(dest)

    if len(files) > 0:
        bf._api.io.upload_files(dest, files, display_progress=True)
    for d in dirs:
        name = os.path.basename(os.path.normpath(d))
        print 'Uploading to {}'.format(name)
        c = Collection(name)
        parent = bf.get(dest)
        parent.add(c)
        files = [os.path.join(d,f) for f in os.listdir(d) if not f.startswith('.')]
        recursively_upload(bf,c.id,files)

def get_client():
    from blackfynn import Blackfynn

    try:
        bf = Blackfynn()
        return bf
    except:
        exit("Unable to authenticate against Blackfynn using the specified API token.")
