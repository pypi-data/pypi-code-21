import glob
import os


def get(l: list, idx: int, default):
    return l[idx] if len(l) > idx else default


def remove_path_ext(p: str):
    return get(p.rsplit('.', 1), 0, default=p)


def filename_at(path: str):
    basename = os.path.basename(path)
    return os.path.splitext(basename)[0]


def path_ext(p: str):
    return get(p.rsplit('.', 1), 1, default=p)


def is_png_img(path: str):
    return os.path.isfile(path) and path_ext(path) == 'png'


def gather_pngs_in(path: str):
    return glob.glob(path + '/*.png')
