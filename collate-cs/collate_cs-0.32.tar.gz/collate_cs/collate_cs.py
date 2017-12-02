import get_src
import write_src

def _(before_path, after_path, namespace_depth, prefix):
    src = get_src._(before_path, namespace_depth, prefix)
    write_src._(src, after_path, namespace_depth)
