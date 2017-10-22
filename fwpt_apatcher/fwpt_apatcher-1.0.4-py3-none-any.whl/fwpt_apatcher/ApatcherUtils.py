import glob
import logging
import os
import shutil
import sys
import time
import zipfile

from fw_patches2.module_prepare import prepare

logger = logging.getLogger(__name__)
zip_log_name = "archlogs.zip"


# разбиение списка файлов на две категории - бд и веб
def split_list_files(lmass):
    lm_db = []
    lm_web = []
    for item in lmass:
        if "flexy-" in item:
            lm_web.append(item)
        else:
            lm_db.append(item)

    lm_db.sort()
    lm_web.sort()

    return lm_db, lm_web


# получение содержимого файла целиком
def get_full_txt(path_to):
    with open(path_to) as f:
        data = f.read().replace('\n', '')
    return data


# получение шапки патча
def get_patch_top_txt(path_to):
    data = get_full_txt(path_to)
    patch_body = data[data.find("/*") + 1: data.find("*/")]
    return patch_body


# парсинг переданных номеров патчей для получения интервалов
def parse_nums_patches_interval(sarg_line):
    sdk_num = sarg_line[sarg_line.find("s:") + 2: sarg_line.find(",", sarg_line.find("s:"))]
    base_num = sarg_line[sarg_line.find("b:") + 2: sarg_line.find(",", sarg_line.find("b:"))]
    proj_num = sarg_line[sarg_line.find("p:") + 2: sarg_line.find(",", sarg_line.find("p:"))]
    try:
        p1 = [int(sdk_num.split("-", 1)[0])] if len(sdk_num.split("-", 1)) < 2 else list(
            range(int(sdk_num.split("-", 1)[0]), int(sdk_num.split("-", 1)[1]) + 1))
    except ValueError:
        p1 = []
    try:
        p2 = [int(base_num.split("-", 1)[0])] if len(base_num.split("-", 1)) < 2 else list(
            range(int(base_num.split("-", 1)[0]), int(base_num.split("-", 1)[1]) + 1))
    except ValueError:
        p2 = []

    try:
        p3 = [int(proj_num.split("-", 1)[0])] if len(proj_num.split("-", 1)) < 2 else list(
            range(int(proj_num.split("-", 1)[0]), int(proj_num.split("-", 1)[1]) + 1))
    except ValueError:
        p3 = []

    return p1, p2, p3


# получение полного списка файлов - патчей для включения в документацию
def get_all_patch_files_by_nums(p_dir_sdk, p_dir_base, p_dir_proj, p_sdk=None, p_base=None, p_proj=None):
    fl_lst = []
    fl_sdk = []
    fl_base = []
    fl_proj = []
    # начнем обход папок для поиска патчей
    if p_dir_sdk != "":
        for p in p_sdk:
            xname = p_dir_sdk + "\\**\\*_*{0}.sql".format(str(p))
            lst_tm = glob.glob(xname, recursive=True)
            fl_lst += lst_tm
            fl_sdk += lst_tm
    if p_dir_base != "":
        for p in p_base:
            xname = p_dir_base + "\\**\\*_*{0}.sql".format(str(p))
            lst_tm = glob.glob(xname, recursive=True)
            fl_lst += lst_tm
            fl_base += lst_tm
    if p_dir_proj != "":
        for p in p_proj:
            xname = p_dir_proj + "\\**\\*_*{0}.sql".format(str(p))
            lst_tm = glob.glob(xname, recursive=True)
            fl_lst += lst_tm
            fl_proj += lst_tm

    fl_sdk = sorted(list(set(fl_sdk)))
    fl_base = sorted(list(set(fl_base)))
    fl_proj = sorted(list(set(fl_proj)))
    logger.debug("Get files sdk:\n{0};\nbase:\n{1};\nproject:\n{2}\n".format(fl_sdk, fl_base, fl_proj))
    return fl_lst, fl_sdk, fl_base, fl_proj


# вызов создания патча из fw_patches
def make_patch_f(args):
    print(args)
    # изменим окружение
    old_sys_argv = sys.argv
    sys.argv = [old_sys_argv[0]] + args
    prepare()
    # вернём как было
    sys.argv = old_sys_argv


# периодическое сжатие логов
def zip_old_logs(logdir, critdays=7):
    current_time = time.time()

    if not os.path.exists(os.path.join(logdir, zip_log_name)):
        zarch = zipfile.ZipFile(os.path.join(logdir, zip_log_name), "w")
    else:
        zarch = zipfile.ZipFile(os.path.join(logdir, zip_log_name), "a")

    for f in os.listdir(logdir):
        creation_time = os.path.getctime(os.path.join(logdir, f))
        if (current_time - creation_time) // (24 * 3600) >= int(critdays) and "main" not in f:
            zarch.write(os.path.join(logdir, f), os.path.basename(os.path.join(logdir, f)))
            os.remove(os.path.join(logdir, f))
            logger.info('File {} replaced to zip log file.'.format(f))
            logger.info('File {} removed from log directory.'.format(f))
    return 0


# копирование файлов в папку
def copy_patches_to_dir(ldir, lpatches):
    if len(lpatches) == 0:
        return
    os.makedirs(ldir)

    for x in lpatches:
        dist = os.path.join(ldir, x.split("\\")[-1])
        shutil.copyfile(x, dist)


# подготовка файлов к передаче
def prepare_transferring_customer(lconf, transfer_objects, ldir, docs):
    root_dir = lconf.customer_path["prepare_dir"]
    if not os.path.isdir(root_dir):
        logger.info("Customer directory not exists -> Create directory {}".format(root_dir))
        os.makedirs(root_dir)

    target_dir = os.path.join(root_dir, ldir)
    if os.path.exists(target_dir):
        logger.warning("{} directory found -> Overwriting".format(target_dir))
        shutil.rmtree(target_dir)
    os.makedirs(target_dir)

    for dir_key in transfer_objects.keys():
        copy_patches_to_dir(os.path.join(target_dir, lconf.customer_path[dir_key.lower()]), transfer_objects[dir_key])

    logger.info("Copying patch documents ...")
    copy_patches_to_dir(os.path.join(target_dir, lconf.customer_path["docs"]), docs)
    logger.info("Customer directory {} was successfully prepared".format(target_dir))
