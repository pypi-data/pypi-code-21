# coding=utf-8
import logging
import os
import os.path
import shutil


def should_update(src_file, dest_file):
    try:
        sink_st = os.stat(src_file)
    except FileNotFoundError:
        logging.error("Fail to retrieve information about sink %s (skip update)", src_file)
        return False

    sink_sz = sink_st.st_size
    sink_mt = sink_st.st_mtime

    try:
        target_st = os.stat(dest_file)
    except FileNotFoundError:
        logging.error("Fail to retrieve information about target %s (skip update)", dest_file)
        return False

    target_sz = target_st.st_size
    target_mt = target_st.st_mtime

    if target_sz != sink_sz:
        return True

    return target_mt != sink_mt


def copy_file(src_file, dest_file):
    logging.debug("copy: %s to: %s", src_file, dest_file)

    try:
        shutil.copyfile(src_file, dest_file)
    except IOError:
        logging.error("Fail to copy %s", src_file)

    try:
        s = os.stat(src_file)
        os.utime(dest_file, (s.st_atime, s.st_mtime))
    except IOError:
        logging.error("Fail to copy timestamp of %s", src_file)


def copy_from_to(src_root, src_files, dest):
    for src_name in src_files:
        rel_path = os.path.relpath(src_name, src_root)

        dest_file = os.path.join(dest, rel_path)

        if os.path.isfile(dest_file) and not should_update(src_name, dest_file):
            continue

        dest_dir_name = os.path.dirname(dest_file)

        if not os.path.isdir(dest_dir_name):
            os.makedirs(dest_dir_name, exist_ok=True)

        copy_file(src_name, dest_file)
