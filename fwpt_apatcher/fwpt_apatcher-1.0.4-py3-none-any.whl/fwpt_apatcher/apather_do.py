import argparse
import configparser
import datetime
import json
import locale
import logging
import os
import sys
import time

from pymorphy2 import MorphAnalyzer

import fwpt_apatcher.ApatcherClass as ac
import fwpt_apatcher.ApatcherGDocs as agd
import fwpt_apatcher.ApatcherMenu as amenu
import fwpt_apatcher.ApatcherUtils as autil

__version__ = "1.0.4"
debug_mode = False

logging.basicConfig(filename="back/ct_main.log",
                    level=logging.INFO,
                    format='[%(asctime)s][%(levelname)s] %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S',
                    filemode="a+")
locale.setlocale(locale.LC_ALL, "ru")


# Не будем городить класс для парсера, т.к. argparse создает его внутри методов.
def create_parser():
    parser = argparse.ArgumentParser(
        prog="apatcher_forward",
        description="Автоматизированная сборка template патча и сопровождающей документации",
        epilog="(c) Alex1OPS.",
        add_help=False
    )
    # группа параметров
    parent_group = parser.add_argument_group(title="Параметры")
    parent_group.add_argument("-p", "--project", help="Проект")
    parent_group.add_argument("-k", "--manual", help="Жесткая передача всех данных для формирования")
    parent_group.add_argument("-c", "--commit", action='store_true', default=False, help="Флаг коммита после сборки")
    parent_group.add_argument("-n", "--nomake", action='store_true', default=False, help="Флаг сборки патча")
    parent_group.add_argument("-d", "--docs", action='store_true', default=False,
                              help="Флаг генерации сопровождающих документов")
    parent_group.add_argument("-o", "--only", action='store_true', default=False,
                              help="Только генерация сопровождающих документов")
    parent_group.add_argument("-a", "--anum", help="Номера патчей для добавления документации")
    parent_group.add_argument("-f", "--fwopt", help="Ключи для стандартной патчилки")
    parent_group.add_argument("-r", "--dir", default="", help="Папка, в которой будет передан патч")
    parent_group.add_argument("-t", "--text", default="Empty comment line", help="Текст комментария к коммиту")
    parent_group.add_argument("-e", "--edit", action='store_true', default=False,
                              help="Флаг редактирования списка файлов")
    parent_group.add_argument("-m", "--make", action='store_true', default=False,
                              help="Только создание патча")
    parent_group.add_argument("--customer", action='store_true', default=False,
                              help="Подготовить к передаче заказчику")
    parent_group.add_argument("-h", "--help", action="help", help="Справка")
    parent_group.add_argument("--version",
                              action="version",
                              help="Номер версии",
                              version="%(prog)s {}".format(__version__))
    return parser


def generate_process_doc_patch(namespace):
    # настроим морфологический анализатор
    morph = MorphAnalyzer()
    # текущая дата в виде строки
    dt_make = datetime.date.today()
    # получим месяц в родительном падеже
    dt_str_make = ""
    try:
        dt_str_make = dt_make.strftime(u"%d " + morph.parse(dt_make.strftime(u"%B"))[0].inflect({'gent'}).word + " %Y")
    except Exception as e:
        logging.error(e)
        logging.info(dt_str_make)
        exit(0)

    tcfg_arg = None
    path_dir = None
    try:
        tcfg_arg = ac.CfgInfo()
        if namespace.project:
            path_dir = tcfg_arg.path.get("projects_path", namespace.project)
        else:
            logging.warning("path_dir to project is empty")
            path_dir = ""
        if not os.path.isdir(path_dir) and namespace.project:
            logging.error("Can\'t find directory for project = {0}".format(namespace.project))
            raise Exception("Can\'t find directory for project", namespace.project)
    except configparser.NoOptionError:
        logging.error("Config file parse error")
        print("Config file parse error")
        exit(0)
    except Exception as inst:
        logging.error("Unknown error: {0}".format(inst))
        print(inst)
        exit(0)
    # отобразим конфигурацию
    if debug_mode is True:
        print("Configuration: ")
        print("  Only docs -> {}".format(str(namespace.only)))
        print("  Can edit -> {}".format(str(namespace.edit)))
        print("  Create docs (patch mode) -> {}".format(str(namespace.docs)))
        print("  With preparing for transferring to customer -> {}".format(str(namespace.customer)))

    transfer_objects = {}

    if namespace.only is False:
        # получим статусы объектов в репо
        topl = ac.RepoJob(path_dir=path_dir)
        objects_new, objects_mod, objects_del, objects_unchecked = topl.parse_status(topl.get_status())
        if namespace.edit is True:
            objects_new, objects_mod, objects_del = amenu.edit_files_list(new_lm=objects_new, mod_lm=objects_mod,
                                                                          del_lm=objects_del)
        list_files = [] + objects_new + objects_mod

        # если ручной режим
        if namespace.manual is not None:
            objects_new = objects_del = []
            list_files = objects_mod = namespace.patch_files

        # разберем статусы объектов репо по полям патча
        fin_p = ac.Patch(author=tcfg_arg.author, comment=namespace.text,
                         objects_new=", ".join([p.rsplit("\\", 1)[-1] for p in objects_new]),
                         objects_mod=", ".join([p.rsplit("\\", 1)[-1] for p in objects_mod]),
                         objects_del=", ".join([p.rsplit("\\", 1)[-1] for p in objects_del]),
                         files_list="\n".join(["@@ " + p for p in list_files]), before_script=namespace.before_script)
        fin_p.take_from()
        fin_p.prepare(proj_name=namespace.project)
        fin_p.save(path_to_file=os.path.join(path_dir, "patch-template/template.sql"))

        # соберем патч
        if namespace.nomake is False or namespace.make is True:
            b_sucs_making = fin_p.make_patch_fw(path_to_file=os.path.join(path_dir, "patch-template/template.sql"),
                                                root_path=path_dir,
                                                fwoption=namespace.fwopt)
            if b_sucs_making is True:
                print("Making patch -> Success")
            else:
                print("Making patch -> Fail")

        # если нужно, отправим коммит
        if namespace.commit is True:
            topl.send_commit(comment_line=fin_p.comment)

        # если нужно, соберем сопровождающие документы
        if namespace.docs is True and namespace.nomake is False:
            # получим статус репо - ожидаем там увидеть патч
            ts_rp_patch = ac.RepoJob(path_dir=path_dir + "\\patches")
            objects_new_p, objects_mod_p, objects_del_p, objects_unch_p = ts_rp_patch.parse_status(
                ts_rp_patch.get_status(),
                b_patch=True)

            proj_name = path_dir.split("/")[-1]
            latest_ver = str(os.path.basename(objects_new_p[0]))
            latest_ver = latest_ver[11:latest_ver.index(".sql")]
            namespace.anum = "[{proj}:{ver}]".format(proj=proj_name, ver=int(latest_ver))

    pr_docs = []
    if (namespace.only is False and namespace.docs is True and namespace.nomake is False) or namespace.only:
        l_pc = agd.parse_namespace_pc(namespace.anum, root_path=tcfg_arg.root_path)
        for i in l_pc: i.prepare()
        for i in l_pc: logging.debug(i)

        doc_changelist = agd.DocEntity(doc_name="changelist.docx", ext=agd.ExtNameDocTpl.CHANGELIST, projects=l_pc,
                                       customer_dir=namespace.dir, print_author=tcfg_arg.prepauthor,
                                       date_str=dt_str_make)
        doc_update_log = agd.DocEntity(doc_name="update_log.docx", ext=agd.ExtNameDocTpl.UPDATE_LOG, projects=l_pc,
                                       customer_dir=namespace.dir, print_author=tcfg_arg.prepauthor,
                                       date_str=dt_str_make)

        doc_changelist.generate()
        doc_update_log.generate()

        pr_docs = [doc_changelist.get_doc_path(), doc_update_log.get_doc_path()]
        for x in l_pc: transfer_objects[x.project_ext] = x.get_objects_for_transfer()

    if namespace.customer and len(pr_docs) != 0:
        autil.prepare_transferring_customer(lconf=tcfg_arg,
                                            transfer_objects=transfer_objects,
                                            ldir=namespace.dir,
                                            docs=pr_docs)


def main():
    start_exec_time = time.time()
    log_dir = "back"
    tmp_dir = "tmp"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    # получим аргументы командной строки
    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])
    logging.info(sys.argv)

    try:
        # если ручной режим, то парсим полученный json
        if namespace.manual is not None:
            with open(namespace.manual, encoding="utf-8") as data_file:
                data = json.load(data_file)
            namespace.project = data['project']
            namespace.text = data['comment']
            namespace.docs = data['with_docs']
            namespace.only = data['only_docs']
            if namespace.docs is True or namespace.only:
                namespace.dir = data['dirprep'].strip("/")
                namespace.customer = data['prep_customer']
                namespace.anum = data['prepdocs']
            namespace.before_script = data['scripts']
            namespace.patch_files = data['patch_files']
        else:
            namespace.before_script = ""
    except Exception as inst:
        logging.error("I couldn't find json file {0} in manual mode: {1}".format(namespace.manual, inst))
        print(inst)
        exit(0)

    generate_process_doc_patch(namespace)

    elapsed_time = time.time() - start_exec_time
    print("Runtime: {0} sec".format(round(elapsed_time, 3)))
    logging.info("Runtime: {0} sec".format(round(elapsed_time, 3)))


if __name__ == "__main__":
    main()
