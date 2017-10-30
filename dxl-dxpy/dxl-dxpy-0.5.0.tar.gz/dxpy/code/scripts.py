def path_of_script_folder_of_module(module, relative_path='../scripts'):
    from dxpy.filesystem import Path
    return Path(Path(module.__file__) / relative_path)
