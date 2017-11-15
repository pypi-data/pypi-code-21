def path_of_script_folder_of_module(module, relative_path='../scripts'):
    from dxpy.filesystem import Path
    return Path(Path(module.__file__) / relative_path)


def path_of_global_defaults(root_module='dxpy'):
    from dxpy.filesystem import Path
    return Path(Path('~') / '.{m}'.format(m=root_module))
