"""
Filesystem web resources

APIs provided:
    <root>/fs/file/<path>
    <root>/fs/files/<path>
    <root>/fs/dir/<path>
    <root>/fs/dirs/<path>
    <root>/fs/path/<path>
"""


def add_api(api, root, name='fs'):
    from .path.web import add_api as add_path_api
    from .file.web import add_api as add_file_api
    from .directory.web import add_api as add_dir_api
    root_fs = root + '/{0}'.format(name)
    add_path_api(api, root_fs)
    add_file_api(api, root_fs)
    add_dir_api(api, root_fs)
