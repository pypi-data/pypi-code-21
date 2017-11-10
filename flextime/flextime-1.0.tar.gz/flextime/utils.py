import yaml, os.path

from functools import reduce

def guess_path(tree, words):
    def build_path(acc, word):
        tree, path_parts = acc

        path_parts[-1].append(word)

        key = ' '.join(path_parts[-1])
        if key in tree:
            tree = tree[key]
            #path_parts[-1] = key 
            path_parts.append([])

        return (tree, path_parts)

    tree, path_lists = reduce(build_path, words, (tree, [[]]))
    return [' '.join(p) for p in path_lists if p]
    
def file_to_dict(filename):
    if os.path.isfile(filename):
        with open(filename) as f:
            return yaml.safe_load(f)
    else:
        print("{} not found; skipping.".format(filename))

def date_to_str(d):
    date_format = '%m-%d-%Y'
    return d.strftime(date_format)


def dump_dict(d):
    noalias_dumper = yaml.dumper.SafeDumper
    noalias_dumper.ignore_aliases = lambda self, date: True
    return yaml.dump(d, default_flow_style=False, Dumper=noalias_dumper)
           
