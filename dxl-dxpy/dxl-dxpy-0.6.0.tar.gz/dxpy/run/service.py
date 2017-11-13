from dxpy.filesystem import Path, File


def get_scripts_path():
    import dxpy
    dxpy_init_file = dxpy.__file__
    path_dxpy = Path(dxpy_init_file).father
    path_scripts = Path(path_dxpy) / 'scripts'
    return path_scripts


def get_script(name):
    path_scripts = get_scripts_path()
    possible_suffix = ['', '.sh', '.py']
    for s in possible_suffix:
        path_file = path_scripts / name + s
        if File(path_file).exists:
            break
    return path_file
