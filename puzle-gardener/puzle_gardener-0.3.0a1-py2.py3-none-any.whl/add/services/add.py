import shutil
from pathlib import Path


import yaml


def check_seed_config(path: Path):
    result: bool = True

    seed_config_path = Path(path, 'puzle-seed.yml')
    if not seed_config_path.exists():
        result = False
    else:
        data = yaml.safe_load(seed_config_path.read_text())
        if 'name' not in data:
            result = False

    return result

def add(current_path: Path, seed_path: Path, override: bool = False ):
    if current_path is str:
        current_path = Path(current_path)

    if seed_path is str:
        seed_path = Path(seed_path)

    seed_paste_path = Path(seed_path, current_path.name)

    print('The seed to copy:', current_path.absolute())
    print('The seed destination:', seed_paste_path.absolute())


    # Check if paths are correct

    if not current_path.exists():
        raise FileNotFoundError(current_path)
    else:
        if not current_path.is_dir():
            raise ValueError("The current path to copy must be a valid directory")

    if not seed_path.exists():
        raise FileNotFoundError(seed_path)
    else:
        if not seed_path.is_dir():
            raise ValueError("The seed destination path must be a valid directory")

    if not check_seed_config(current_path):
        raise ValueError("The 'puzle-seed.yml' file is not valid")

    # Check if the seed already exist

    if seed_paste_path.exists():
        if not override:
            raise FileExistsError("The seed exist already, if you want to override it, try with the flag -f")
        else:
            try:
                print("remove",seed_paste_path)
                shutil.rmtree(seed_paste_path.absolute().__str__())
            except Exception:
                raise RuntimeError("cannot remove the existing seed folder")

    # Copy the file
    try:
        print("Copy the seed into the global location")
        shutil.copytree(current_path.absolute().__str__(), seed_paste_path.absolute().__str__())
    except OSError as exc: # python >2.5
        raise RuntimeError('Cannot copy the folder:', current_path)

    print("The seed is now duplicated in the global location!")
