# -*- coding: utf-8 -*-
import random
import string
import traceback
import bgionline
import bgionline.api
from bgionline.utils import prettytable
import platform
import sys
import time
import os
import json
import oss2
import types
import psutil
import collections
import base64
import Queue
import math

OSTYPE = platform.system().lower()
LAST_PERCENT = -1
LAST_TIME = -1
LAST_CONSUMED = -1


def try_call(func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except Exception as e:
        print(traceback.print_exc(e))


def forge_random_string():
    return "".join([random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(16)])


def get_fully_path(path, is_end=True):
    """
    :param path: 传入的路径
    :param is_end: 返回的路径是否需要用‘/’结尾
    :return: 返回完整的路径
    """
    if path == '' or path == './' or path == '.' or path is None:
        if is_end or bgionline.config.current_wd is '/':
            return to_zhcn(bgionline.config.current_wd)
        else:
            return to_zhcn(bgionline.config.current_wd[:-1])
    if path[0] != '/':
        path = to_zhcn(bgionline.config.current_wd) + path
    if is_end and path[-1] != '/':
        path += '/'
    elif not is_end:
        if path != '/':
            if path[-1] is '/':
                path = path[:-1]
    return (to_zhcn(path)).encode("utf-8")


def get_next_path(path, path_list):
    new_path_list = []
    if path.endswith('/'):
        for i in path_list:
            if i.startswith(path):
                try:
                    new_path_list.append(path + (i.partition(path)[2]).partition('/')[0])
                except:
                    pass
    else:
        for i in path_list:
            if i.startswith(path):
                try:
                    new_path = path + i.partition(path)[2].split('/')[0]
                    if new_path != i:
                        new_path += '/'
                    new_path_list.append(new_path)
                except:
                    pass
    return list(set(new_path_list))


def choices_project(projects, show_info=['id', 'name'], show_info_name=None, default_choices_id=None):
    """
    提供选择的方法
    :param projects: 被选择的对象
    :param show_info: 被选择对象需要显示的字段，默认是['id','name']
    :param show_info_name: 被现在对象的的信息表头，如果没有输入，默认是和字段一样
    :param default_choices_id: 默认选中的id
    :return: 选择的结果
    """
    prev = 0
    if show_info_name is None:
        td = show_info[0:]
    else:
        td = show_info_name[0:]
    td.insert(0, 'index')

    table = prettytable.PrettyTable(td, padding_width=1, align="l")
    for i in td[1:]:
        table.align[i] = "l"
    for index, p in enumerate(projects):
        row = [index]
        for i in show_info:
            if i == 'size':
                row.append(parse_size(p[i], format=False, format_int=2))
            elif i == 'createdAt':
                row.append(format_time(p[i]))
            else:
                row.append(to_zhcn(p[i]))
        table.add_row(row)
        if default_choices_id is not None and p.get('id') == default_choices_id:
            prev = index
    # end for
    print table

    while True:
        pick = None
        try:
            if default_choices_id is not None:
                pick = raw_input("Pick a numbered choice [%s]: " % prev)
            else:
                pick = raw_input("Pick a numbered choice :")
        except (KeyboardInterrupt, EOFError), e:
            bgionline.exceptions.err_exit("Keyboard Interrupted.")
        except Exception, e:
            print("Not a valid selection")
            continue

        if pick is "":
            pick = prev
            return pick

        try:
            pick = int(pick)
            if not pick in range(index + 1):
                print("Not a valid selection")
            else:
                return pick
        except Exception, e:
            print("Not a valid selection")
            pass


def to_zhcn(msg):
    """
    解决windows中文下无法正常显示
    :param msg:
    :return:
    """
    if type(msg) is types.IntType:
        return msg
    os_codepage = sys.getfilesystemencoding()

    if OSTYPE == "windows":
        try:
            return msg.decode('utf8').encode(os_codepage)
        except:
            try:
                return msg.encode()
            except:
                pass
    return msg


def parse_size(size, format=True, format_int=0):
    """
    解析大小的单位
    :param size: 单位为 B
    :return:
    """
    size = float(size)
    if size < 0:
        size = 0
    unit = [' B', 'KB', 'MB', 'GB', 'TB', 'PB']
    div = 0
    while size >= 1024.0:
        size /= 1024.0
        div += 1
    if format:
        return '%6.1f  %s' % (round(size, format_int), unit[div])
    else:
        return '%.2f  %s' % (round(size, format_int), unit[div])


def progress(consumed, total):
    """
    oss 进度回调
    :param consumed: 已下载大小
    :param total: 总大小
    :return:
    """
    global LAST_PERCENT
    global LAST_TIME
    global LAST_CONSUMED
    percent = round(consumed * 1.0 / total * 100, 2)
    new_time = time.time()
    if LAST_TIME != -1:
        try:
            sys.stdout.write(" [%s%s]    %s/s\r" % (
                '=' * int(percent / 2), (' ' * (50 - int(percent / 2))),
                parse_size(((consumed - LAST_CONSUMED) / (new_time - LAST_TIME)))))
            # sys.stdout.flush()
        except Exception, e:
            pass
        if LAST_PERCENT == 100:
            LAST_PERCENT = -1
            LAST_TIME = -1
            LAST_CONSUMED = -1
    else:
        sys.stdout.write("[%s%s]\r" % (
            '=' * int(percent / 2), (' ' * (50 - int(percent / 2)))))
        sys.stdout.flush()
    LAST_PERCENT = percent
    LAST_TIME = new_time
    LAST_CONSUMED = consumed


def get_sts_token(refresh=False):
    if refresh or time.time() - float(bgionline.config.sts_token_time) > 2000:
        try:
            token = bgionline.api.get_sts_token()
            bgionline.config.sts_token = json.dumps(token.get('credentials'))
            bgionline.config.sts_token_time = time.time()
            bgionline.config.save()
        except Exception as e:
            print e
    return json.loads(bgionline.config.sts_token)


def parse_time(time):
    """
    解析时间函数
    :param time:单位秒
    :return:
    """
    m, s = divmod(time, 60)
    h, m = divmod(m, 60)
    if h > 9999:
        h = 9999
    return "%4d:%02d:%02d" % (h, m, s)


def get_files_info(path, name=[]):
    """
    统计文件的大小
    :param path:需要统计的文件、文件夹 的路径
    :return: 文件的大小
    """
    count = 0
    size = 0L
    if os.path.isfile(path):
        count = 1
        size = os.stat(path)[6]
        name.append(path)
    elif os.path.isdir(path):
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            item_count, item_size, name = get_files_info(item_path)
            count += item_count
            size += item_size
    return count, size, name


def calculate_file_crc64(file_name, block_size=64 * 1024, init_crc=0):
    """
    计算CRC
    :param file_name:
    :param block_size:
    :param init_crc:
    :return:
    """
    with open(file_name, 'rb') as f:
        crc64 = oss2.utils.Crc64(init_crc)
        while True:
            data = f.read(block_size)
            if not data:
                break
            crc64.update(data)

    return crc64.crc


def multiprocessing_daemon(multiprocessing, queue, list_pid, function, record_dict, record_f, lock, consumed, err_file,
                           succeed_file, print_location):
    while not queue.empty():
        for i in list_pid:
            try:
                new_process = 0
                proc = psutil.Process(i)
                if proc.status() == psutil.STATUS_ZOMBIE:
                    new_process = 1
            except:
                new_process = 1
            finally:
                if new_process:
                    try:
                        os.kill(i, 9)
                    except:
                        pass
                    if not queue.empty():
                        list_pid.remove(i)
                        cons = multiprocessing.Process(target=function,
                                                       args=(
                                                           queue, record_dict, record_f, lock,
                                                           consumed, err_file,
                                                           succeed_file, (0, print_location[i])))

                        cons.daemon = True
                        cons.start()
                        list_pid.append(cons.pid)
                        print_location[cons.pid] = print_location[i]
                        print_location.pop(i)
        time.sleep(0.1)


if OSTYPE != "windows":
    from blessings import Terminal

    TERM = Terminal()


    class Writer(object):
        """Create an object with a write method that writes to a
        specific place on the screen, defined at instantiation.
        """

        def __init__(self, location):
            """
            Input: location - tuple of ints (x, y), the position
                              of the bar in the terminal
            """
            self.location = location

        def write(self, string):
            with TERM.location(*self.location):
                print(string)


def set_config(func):
    """
    设置配置文件解析器
    :param func: 函数
    :return:
    """
    try:
        def _set_confg(args):
            if args.config is not None:
                bgionline.config.read_config(args.config)
            func(args)
    except KeyboardInterrupt:
        pass

    return _set_confg


def del_punctuation(strs):
    """
    去掉多余字符
    :param strs: 需要处理的字符串
    :return:
    """
    try:
        del_str = """!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~' '~！@#￥%……&*（）——+=-·{}|、】【’；：“《》，。？、."""
        return strs.translate(string.maketrans('', ''), del_str)
    except:
        return (base64.b64encode(strs))[0, 240]


def format_tree(tree, root=None):
    """
    格式化树形格式
    ({'foo': 0, 'bar': {'xyz': 0}}))

    """
    formatted_tree = [root] if root is not None else []

    def _format(tree, prefix='    '):
        nodes = list(tree.keys())
        for i in range(len(nodes)):
            node = nodes[i]
            if i == len(nodes) - 1 and len(prefix) > 1:
                my_prefix = prefix[:-4] + '└──'
                my_multiline_prefix = prefix[:-4] + '    '
            else:
                my_prefix = prefix[:-4] + '├──'
                my_multiline_prefix = prefix[:-4] + '│   '
            n = 0
            for line in node.splitlines():
                if line == 'node' and line == 'id':
                    continue
                if n == 0:
                    formatted_tree.append(to_zhcn(my_prefix) + line)
                else:
                    formatted_tree.append(to_zhcn(my_multiline_prefix) + line)
                n += 1

            if isinstance(tree[node], collections.Mapping):
                subprefix = prefix
                if i < len(nodes) - 1 and len(prefix) > 1 and prefix[-4:] == '    ':
                    subprefix = prefix[:-4] + '│   '
                _format(tree[node], subprefix + '    ')

    _format(tree)
    return '\n'.join(formatted_tree)


def format_time(time_stamp):
    """
    格式话时间戳
    :param time_stamp:时间戳
    :return: xxxx-xx-xx xx:xx:xx
    """

    time_array = time.localtime(time_stamp)
    return time.strftime("%Y-%m-%d %H:%M:%S", time_array)


def split_project_path(path_str):
    """
    分离出项目和路径
    :param path_str: 路径
    :return: 项目，路径
    """
    project = None
    if path_str.count(':') > 1:
        print 'This is erroe path'
        sys.exit(-1)
    if ':' in path_str:
        project, path = path_str.split(':')
        if path is '':
            path = '/'
    else:
        path = get_fully_path(path_str)
    return project, path


class Chunk:
    num = 0
    offset = 0
    len = 0

    def __init__(self, n, o, l):
        self.num = n
        self.offset = o
        self.len = l


def init_queue(filesize):
    # 计算分片的大小，目前100M一片，单位为字节（b）
    if filesize > 103809024000:
        chunk_size = filesize / 950
    else:
        chunk_size = 104857600
    chunkcnt = int(math.ceil(filesize * 1.0 / chunk_size))
    q = Queue.Queue(maxsize=chunkcnt)
    for i in range(0, chunkcnt):
        offset = chunk_size * i
        len = min(chunk_size, filesize - offset)
        c = Chunk(i + 1, offset, len)
        q.put(c)
    return q
