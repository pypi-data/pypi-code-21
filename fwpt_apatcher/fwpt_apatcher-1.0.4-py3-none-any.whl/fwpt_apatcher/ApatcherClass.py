import configparser as cfg
import datetime
import logging
import os
import subprocess
import sys

import fwpt_apatcher.ApatcherUtils as autil

logger = logging.getLogger(__name__)

PATH_TO_IMG = "cfg/box_img.jpg"
PATH_TO_TMPL = "cfg/_temp.sql"
PATH_TO_CFG = "cfg/config.ini"
WARNING_MSG_DELIMITER = ">>>"


class PatchBase:
    def __init__(self, author=None, date=None, num=None, ticket_num=None, objects_new=None, objects_mod=None,
                 objects_del=None, comment=None, files_list=None):
        self.author = author
        self.date = date
        self.num = num
        self.ticket_num = ticket_num
        self.objects_new = objects_new
        self.objects_mod = objects_mod
        self.objects_del = objects_del
        self.comment = comment
        self.files_list = files_list


class Patch(PatchBase):
    name = None
    full = None
    before_script = None

    def __init__(self, author=None, date=None, num=None, ticket_num=None, objects_new=None, objects_mod=None,
                 objects_del=None, comment=None, files_list=None, before_script=None):
        PatchBase.__init__(self, author, date, num, ticket_num, objects_new, objects_mod, objects_del, comment,
                           files_list)
        self.before_script = before_script

    def prepare(self, proj_name="Default"):
        self.name = proj_name
        self.full = self.full.replace("__author__", self.author)
        self.full = self.full.replace("__ticket_num__", "")
        self.full = self.full.replace("__new_objs__", self.objects_new)
        self.full = self.full.replace("__modify_objs__", self.objects_mod)
        self.full = self.full.replace("__del_objs__", self.objects_del)
        self.full = self.full.replace("__comment_body__", self.comment)
        self.full = self.full.replace("__list_objs__", self.files_list)
        self.full = self.full.replace("__project__", self.name)
        self.full = self.full.replace("__before_script__", self.before_script)

    def take_from(self, path_to_file=PATH_TO_TMPL):
        try:
            with open(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), path_to_file), 'r') as fl:
                file_data = fl.read()
            self.full = file_data
        except FileNotFoundError:
            print("Can\'t find a template sql file for make patch")
            exit(0)

    def save(self, path_to_file):
        with open(path_to_file, 'w') as fl:
            fl.write(self.full)

    @staticmethod
    def make_patch(path_to_file):
        cmd = path_to_file
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        out, err = p.communicate()
        result = out.decode("utf-8")
        result = result.split("\n")
        stat_msg = result[-3]

        if "DONE" in stat_msg:
            return True
        else:
            return False

    @staticmethod
    def make_patch_fw(path_to_file, root_path, fwoption):
        dt_str = datetime.datetime.now().strftime("back\\%Y%m%d_%H_%M_%S_fwlog.log")
        orig_stdout = sys.stdout
        f = open(dt_str, 'w+')
        sys.stdout = f

        autil.make_patch_f(args=['--ui', '--template={}'.format(path_to_file), '--root={}'.format(root_path)])

        sys.stdout = orig_stdout
        f.close()
        # получим последнюю строку файла с оценкой в 100 символов для получение статуса патча
        # магические числа плохо, но тут так норм :)
        f = open(dt_str, 'rb')
        f.seek(-100, 2)
        last = f.readlines()[-5].decode()
        print(last)
        f.close()

        return True if "DONE" in last else False


class RepoJob:
    def __init__(self, path_dir=None, objects_new=None, objects_mod=None, objects_del=None):
        self.path_dir = path_dir
        self.objects_new = objects_new
        self.objects_mod = objects_mod
        self.objects_del = objects_del

    # получим статус репо в виде массива строк - 1 на 1 файл репо
    def get_status(self):
        cmd = "svn status " + self.path_dir
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        out, err = p.communicate()
        result = out.decode("utf-8", errors='ignore')
        result = result.split("\n")
        result = [p[:-1] for p in result]
        return result

    # парсинг статуса репо вМс1 в 3 массива новых, изменнных, удаленных объектов
    @staticmethod
    def parse_status(status_mass, b_patch=False):
        obj_new = []
        obj_mod = []
        obj_del = []
        obj_unchecked = []
        # разберем статусы файла, полученные из svn status
        for ptr in status_mass:
            try:
                p_fmt = ptr.split(".", 1)[1]
            except IndexError:
                p_fmt = ""
            if ("patches" in ptr or "template.sql" in ptr) and b_patch is not True:
                continue
            if p_fmt not in ("sql", "pck", "xml", "fnc", "prc", "tps"):
                continue
            if ptr[:1] == 'M':
                obj_mod.append(ptr[1:].lstrip())
            elif ptr[:1] == 'N' or ptr[:1] == 'A':
                obj_new.append(ptr[1:].lstrip())
            elif ptr[:1] == 'D':
                obj_del.append(ptr[1:].lstrip())
            else:
                obj_unchecked.append(ptr[1:].lstrip())
        return obj_new, obj_mod, obj_del, obj_unchecked

    # отправка коммита
    def send_commit(self, comment_line):
        cmd = "svn commit " + self.path_dir + " -m \"" + comment_line + " \""
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        out, err = p.communicate()
        result = out.decode("utf-8", errors='ignore')
        result = result.split("\n")
        result = "\n".join(result)
        return result


class CfgInfo:
    author = None
    prepauthor = None
    path = None
    customer_path = {}

    def __init__(self, path=None, author=None):
        dir = os.path.dirname(os.path.realpath(sys.argv[0]))
        config = cfg.ConfigParser()
        pth_cfg = os.path.join(dir, PATH_TO_CFG)
        config.read(pth_cfg)
        logging.info("Path to cfg file {}".format(pth_cfg))
        self.author = config.get("info", "author")
        self.prepauthor = config.get("info", "prepauthor")
        self.path = config
        self.root_path = config.get("info", "rootDir")
        self.customer_path = dict(config.items('customer_folder'))
