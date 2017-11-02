import os
import shutil

# necessary for python3.3 support for pathlib.Path (not natively supported)

def rmtree(path):
    return shutil.rmtree(str(path))

def copytree(src, dst):
    return shutil.copytree(str(src), str(dst))

def makedirs(path, *args, **kwargs):
    if not os.path.isdir(str(path)):
        return os.makedirs(str(path), *args, **kwargs)

def listdir(path):
    return os.listdir(str(path))

def walk(path):
    return os.walk(str(path))

def fopen(path, mode, *args, **kwargs):
    return open(str(path), mode, *args, **kwargs)


# def list_dir(self, print_files=False, indent=4, max_level=None):
#     tree = ""
#     padding = '|'+' ' * (indent-1)
#     for path, dir, files in walk(self.abspath):
#         rel_path = Path(path).relative_to(self.dir)
#         parts = rel_path.parts
#         level = len(parts)-1
#         if max_level is not None and level > max_level:
#             continue
#         symbol = ''
#         if os.path.isdir(os.path.abspath(path)):
#             symbol = os.sep
#         if not print_files and symbol != os.sep:
#             continue
#         tree += padding * level+parts[-1]+symbol+"\n"
#     print(tree)
#     return tree
