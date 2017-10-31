import os

import shutil

BASE_FOLDER = os.path.dirname(os.path.abspath(__file__).replace('.pyc', '.py'))


def install(dst_folder):
    target_folder = os.path.join(dst_folder, 'Base')

    sup_folder = os.path.abspath(os.path.join(BASE_FOLDER, 'assets', 'src', 'IMC', 'Base'))

    # Running from source tree.
    print('*', target_folder)
    if os.path.isdir(sup_folder):
        shutil.rmtree(target_folder, ignore_errors=True)
        shutil.copytree(sup_folder, target_folder)
        return

    raise RuntimeError("failed to find C++ assets folders")
