# -*- coding: utf-8 -*-
import re
import os
import pprint
import traceback
import mimetypes
import json
import oss2
import bgionline
import sys
import time
import fnmatch
import bgionline.api
from bgionline.utils import get_fully_path, get_sts_token, parse_size, parse_time, init_queue
from bgionline import logger
from bgionline.exceptions import err_exit
from config import UPLOAD_THREADS_NUM, PART_SIZE, MULTIPART_THRESHOLD
from bgionline.utils import OSTYPE, progress as progres, to_zhcn, del_punctuation
import boto3
import threading
import signal
import Queue
import math

MULTIPROCESSING_CONSUMED = 0
LAST_PERCENT = -1
ERR_FILE = []
SUCCEED_FILE = []
WRITER = ''
FILE_NAME = ''

import logging

custom_logger = logging.getLogger('oss2')
oss2.defaults.logger = custom_logger

custom_logger.addHandler(logging.StreamHandler(sys.stdout))
custom_logger.setLevel(logging.WARNING)

if OSTYPE != "windows":
    from bgionline.utils import Writer


    def linux_mac_progress(consumed, total):
        """
        oss 进度回调
        :param consumed: 已下载大小
        :param total: 总大小
        :return:
        """
        global LAST_PERCENT
        global WRITER
        global FILE_NAME
        percent = round(consumed * 1.0 / total * 100, 2)
        # if percent - LAST_PERCENT > 0:
        WRITER.write("[%s%s]    %s    %s\r" % (
            '=' * int(percent / 2), (' ' * (50 - int(percent / 2))), '%4.1f' % (percent) + ' %', FILE_NAME,))
        LAST_PERCENT = percent


def progress(consumed, total):
    """
    oss 进度回调
    :param consumed: 已下载大小
    :param total: 总大小
    :return:
    """
    global MULTIPROCESSING_CONSUMED
    global LAST_PERCENT
    MULTIPROCESSING_CONSUMED.value += (consumed - LAST_PERCENT)
    LAST_PERCENT = consumed


def show_upload_progress(consumed, total, total_files, err_file, succeed_file, list_pid, queue):
    """
        多进程进度条
        :param consumed: 已经下载的大小
        :param total: 需要下载文件的大小
        :param total_files: 需要下载的文件格式
        :param err_file: 下载中出错的文件数
        :param succeed_file: 下载中成功的文件数
        :param list_pid: 多进程的pid列表
        :param queue: 多进程的任务队列
        :return:
    """
    global MULTIPROCESSING_CONSUMED
    MULTIPROCESSING_CONSUMED = consumed
    global LAST_PERCENT

    try:
        while True:
            percent = round(MULTIPROCESSING_CONSUMED.value * 1.0 / total * 100, 2)
            velocity = MULTIPROCESSING_CONSUMED.value - LAST_PERCENT
            if velocity <= 0:
                velocity = 1
            consumed_file = err_file.__len__() + succeed_file.__len__()
            left_time = parse_time((total - MULTIPROCESSING_CONSUMED.value) / velocity)

            if consumed_file == total_files:
                sys.stdout.write("\r[%s%s]\t%s/s\t%s\t[%s/%s]" % (
                    '=' * 50, (' ' * 0), parse_size(0), parse_time(0), consumed_file, total_files))
            else:
                sys.stdout.write("\r[%s%s]\t%s/s\t%s\t[%s/%s]" % (
                    '=' * int(percent / 2), (' ' * (50 - int(percent / 2))), parse_size(velocity), left_time,
                    consumed_file, total_files))
            sys.stdout.flush()
            LAST_PERCENT = MULTIPROCESSING_CONSUMED.value
            time.sleep(1)
    except KeyboardInterrupt:
        for i in list_pid:
            os.kill(i, 9)

        # 退出前清楚队列
        while not queue.empty():
            queue.get()
            queue.task_done()


def upload_file_consumer(q, upload_record, upload_record_f, lock, consumed, err_file, succeed_file, writer,
                         show_progres=None):
    """
    多进程上传的消费函数
    :param q: 任务队列
    :param upload_record: 已经下载的任务记录
    :param upload_record_f: 任务记录文件
    :param lock: 多进程锁
    :param consumed: 已经下载的大小
    :param err_file: 下载出错的文件
    :param succeed_file: 下载成功的文件
    :return:
    """
    global MULTIPROCESSING_CONSUMED
    MULTIPROCESSING_CONSUMED = consumed
    global ERR_FILE
    ERR_FILE = err_file
    global SUCCEED_FILE
    SUCCEED_FILE = succeed_file
    global FILE_NAME

    if OSTYPE != "windows":
        global WRITER
        WRITER = Writer(writer)
        show_progres = linux_mac_progress

    while True:
        data = q.get()
        try:
            if OSTYPE != "windows":
                WRITER.write('%s\r' + ' ' * (120 + len(FILE_NAME)))
            upload_fail = 1
            project_id = data['project_id']
            parent_id = data['parent_id']
            f_path = data['f_path']
            FILE_NAME = os.path.basename(f_path)
            user_meta = data['user_meta']
            metadatafile_dist = data['metadatafile_dist']
            upload_file(upload_record, upload_record_f, lock, project_id, parent_id, f_path,
                        user_meta, metadatafile_dist, show_progres=show_progres, is_concurrent=True)
            upload_fail = 0
        except KeyboardInterrupt:
            # 退出前清楚队列
            while not q.empty():
                q.get()
                q.task_done()
            break
        finally:
            if OSTYPE != "windows":
                WRITER.write('\n')
            q.task_done()
            if upload_fail:
                ERR_FILE.append(data['f_path'])


def upload_file(upload_record, upload_record_f, lock, project_id, parent_id, f_path, user_meta=None,
                metadatafile_dist=None, show_progres=None, is_concurrent=False):
    """
    上传当个文件
    :param upload_record: 已经下载的任务记录
    :param upload_record_f: 任务记录文件
    :param lock: 多进程锁
    :param project_id:需要上传的文件的项目ID
    :param parent_id:文件的BGIonline的parentid
    :param f_path:本地路径
    :param user_meta:文件需要添加的meta_data
    :return:
    """
    file_path_to_be_parsed = f_path.split(os.sep)[-1]
    m = re.search("(\\d\\d)(\\d\\d)(\\d\\d)_(\\S\\d+)_(\\S+)_L(\\d)_(\\S+)_(\\d).fq.gz", file_path_to_be_parsed)
    rg_id = file_path_to_be_parsed
    meta_data = {}

    if m is not None and len(m.groups()) == 8:
        # matched
        values = list(m.groups())
        del values[3]
        values.append(rg_id)
        keys = ("Year", "Month", "Day", "Flowcell", "Lane", "Library", "Pair", "RGID")
        meta_data = dict(zip(keys, tuple(values)))

        for i in keys:
            if i.lower() in user_meta:
                del meta_data[i]

    else:
        dir_to_be_parsed = os.path.basename(os.path.dirname(os.path.abspath(f_path)))
        m = re.search("(\\d\\d)(\\d\\d)(\\d\\d)_I(\\d+)_(\\S+)_L(\\d)_(\\S+)", dir_to_be_parsed)
        rg_id = dir_to_be_parsed
        if m is not None and len(m.groups()) == 7:
            values = list(m.groups())
            del values[3]
            values.append(rg_id)
            keys = ("Year", "Month", "Day", "Flowcell", "Lane", "Library", "RGID")
            meta_data = dict(zip(keys, tuple(values)))
            m = re.search("(\\S+)_L(\\d+)_(\\S+)_(\\d|).fq.gz", file_path_to_be_parsed)

            if m is not None and len(m.groups()) == 4:
                values = list(m.groups())
                if values[3] == "":
                    values[3] = 1
                meta_data.update({"Pair": values[3]})

            for i in keys:
                if i.lower() in user_meta:
                    del meta_data[i]

        else:
            if file_path_to_be_parsed.startswith('CL'):
                if file_path_to_be_parsed.count('_') == 3:
                    m = re.search("(\\S+)_L(\\d+)_(\\S+)_(\\d|).fq.gz", file_path_to_be_parsed)
                    if m is not None:
                        RGID = file_path_to_be_parsed
                        # matched BGISEQ 500
                        values = list(m.groups())
                        values[2] = "_".join([values[0], 'L' + values[1], values[2]])
                        values.append(RGID)
                        keys = ("Slide", "Lane", "Library", "Pair", "RGID")
                        meta_data = dict(zip(keys, tuple(values)))

                        for i in keys:
                            if i.lower() in user_meta:
                                del meta_data[i]

                elif file_path_to_be_parsed.count('_') == 2:
                    m = re.search("(\\S+)_L(\\d+)_(\\d+).fq.gz", file_path_to_be_parsed)
                    if m is not None:
                        RGID = file_path_to_be_parsed
                        values = list(m.groups())
                        v3 = "_".join([values[0], 'L' + values[1], values[2]])
                        v4 = 1
                        values.append(v3)
                        values.append(v4)
                        values.append(RGID)
                        keys = ("Slide", "Lane", "Barcode", "Library", "Pair", "RGID")
                        meta_data = dict(zip(keys, tuple(values)))

                        for i in keys:
                            if i.lower() in user_meta:
                                del meta_data[i]
    if meta_data.has_key('Library'):
        meta_data["Library"] = meta_data["Library"].split("-")[0]
    if user_meta is not "":
        user_meta_data = dict([i.split("=") for i in user_meta[:-1].split('|')])
        meta_data.update(user_meta_data)
        user_meta_data = meta_data
    else:
        user_meta_data = []
    if metadatafile_dist.get(f_path) is not None:
        metadata = metadatafile_dist.get(f_path)
        for i in metadata.keys():
            if metadata[i] is "":
                metadata.pop(i)
        if not user_meta_data:
            user_meta_data = metadata
        else:
            user_meta_data.update(metadata)
    try:
        transmit(upload_record, upload_record_f, lock, project_id, f_path, parent_id, user_meta_data,
                 show_progres=show_progres, is_concurrent=is_concurrent)
    except Exception as e:
        print(traceback.format_exc(e))
        print("Execution failed: %s" % str(e))
        return -1


def transmit(upload_record, upload_record_f, lock, project_id, file_path, parent_id=None, meta_data=None,
             storage_endpoint='aliyun', show_progres=None, is_concurrent=False):
    """
    建立BGIonline上文件信息
    :param upload_record: 已经下载的任务记录
    :param upload_record_f: 任务记录文件
    :param lock: 多进程锁
    :param project_id:需要上传的文件的项目ID
    :param file_path:本地地址
    :param parent_id:文件的BGIonline的parentid
    :param meta_data:文件需要添加的meta_data
    :param storage_endpoint:oss or s3
    :param show_progres:
    :return:
    """

    if OSTYPE == 'windows':
        file_path_key = file_path.decode('windows-1252')
    else:
        try:
            file_path_key = file_path.decode('UTF-8')
        except:
            file_path_key = file_path
    # 判断是否是新的文件
    is_new_file = True
    if upload_record.has_key(file_path_key):
        upload_id = upload_record[file_path_key]['upload_id']
        url = "?isRefresh=true&filters[0][]=id&filters[0][]==&filters[0][]=%s" % upload_id
        try:
            res = bgionline.api.file_list(project_id, url)
        except Exception as e:
            print e
            return
        if len(res['rows']) != 0:
            is_new_file = False
            if upload_record[file_path_key]['status'] == 2:
                print("File %s already uploaded, skip it." % file_path)
                global MULTIPROCESSING_CONSUMED
                global SUCCEED_FILE
                if hasattr(MULTIPROCESSING_CONSUMED, 'value'):
                    MULTIPROCESSING_CONSUMED.value += os.path.getsize(file_path)
                SUCCEED_FILE.append(file_path)
                return
            remote_path = upload_record[file_path_key]['remote_path']
    if is_new_file:
        if parent_id is None or parent_id == 'None':
            parent_id = ""
        if os.path.islink(file_path):
            if not os.path.exists(os.readlink(file_path)):
                print ('%s s a linked file, the file it is linked to does not exist' % file_path)
                return
            if not os.access(os.readlink(file_path), os.R_OK):
                print ('%s Permission denied' % file_path)
                return
        if not os.access(file_path, os.R_OK):
            print ('%s Permission denied' % file_path)
            return
        data = {
            "name": os.path.basename(file_path),
            "size": os.path.getsize(file_path),
            "metadata": meta_data,
            "parentId": parent_id or "",
        }
        headers = {'Content-Type': "application/json;charset=UTF-8", 'Accept': 'application/json'}

        if OSTYPE == 'windows':
            data = json.dumps(data, ensure_ascii=False).encode('utf8')
        else:
            data = json.dumps(data)

        try:
            res = bgionline.api.new_file(project_id, input_params=data, headers=headers)
        except (KeyboardInterrupt, EOFError) as e:
            logger.debug("interrupted by user")
            err_exit("Keyboard Interrupted.")
        except Exception as e:
            err_exit(e)

        upload_id = res['file']['id']
        remote_path = res['remote']['remote_path']

        upload_record[file_path_key] = {
            'upload_id': upload_id,
            'remote_path': remote_path,
            # 1上传中，2上传完成
            'status': 1
        }

        with lock:
            with open(upload_record_f, 'w') as f:
                try:
                    json.dump(upload_record.copy(), f)
                except Exception as e:
                    pass
    try:
        global last_percent
        last_percent = -1

        if bgionline.config.host.endswith("com") or bgionline.config.host == '52.201.214.105':
            s3_upload(file_path, remote_path, is_concurrent)
        else:
            oss_upload(file_path, remote_path, show_progres)
    except Exception, e:
        raise e
    else:
        upload_status = 2  # ok

    data = {
        "fileId": upload_id,
        "status": upload_status
    }
    try:
        bgionline.api.updata_file_status(project_id, input_params=data)
        upload_record[file_path_key] = {
            'upload_id': upload_id,
            'status': 2
        }
        SUCCEED_FILE.append(file_path_key)
        with lock:
            with open(upload_record_f, 'w') as f:
                try:
                    json.dump(upload_record.copy(), f)
                except Exception as e:
                    pass
    except Exception as e:
        err_exit(e)

    if upload_status != 2:
        raise Exception("upload failed")

    return 0


def oss_upload(file_path, remote_path, show_progres=None):
    """
    上传文件到oss
    :param file_path: 本地路径
    :param remote_path: oss上的路劲
    :param show_progres:显示进度函数
    :return:
    """
    if OSTYPE == 'windows':
        file_path = unicode(file_path)
    bucket_name, key_name = remote_path.split("//")[-1].split("/", 1)
    credentials = get_sts_token()
    access_key_id = credentials['AccessKeyId']
    access_key_secret = credentials['AccessKeySecret']
    security_token = credentials['STS_Token']

    filetype, tmp = mimetypes.guess_type(file_path)
    oss_header = {}
    if filetype:
        oss_header['Content-Type'] = filetype
    else:
        oss_header = None

    auth = oss2.StsAuth(access_key_id, access_key_secret, security_token)
    bucket = oss2.Bucket(auth, bgionline.config.storage_host, bucket_name)

    while True:
        try:
            oss2.resumable_upload(bucket, key_name, file_path,
                                  multipart_threshold=MULTIPART_THRESHOLD,
                                  headers=oss_header,
                                  part_size=PART_SIZE,
                                  num_threads=UPLOAD_THREADS_NUM,
                                  progress_callback=show_progres or progress,
                                  store=oss2.ResumableStore(root=bgionline.config.default_config_dir))
            # print('\nDone.')
            break
        except Exception as e:
            if hasattr(e, 'status') and e.status not in [-3, 403]:
                err = str(e)
                if hasattr(e, 'id'):
                    err = e.id + ':   ' + err
                print ('OSS_ERROR: %s' % err)

            credentials = get_sts_token()
            access_key_id = credentials['AccessKeyId']
            access_key_secret = credentials['AccessKeySecret']
            security_token = credentials['STS_Token']

            auth = oss2.StsAuth(access_key_id, access_key_secret, security_token)
            bucket = oss2.Bucket(auth, bgionline.config.storage_host, bucket_name)
            time.sleep(5)


def upload_directory(upload_record_dict, upload_record_f, lock, metadata, metadatafile_dist, queue, project_id,
                     dir_path, user_meta=None, current_path=None, wildcard=None):
    """
    上传文件夹
    :param queue: 任务队列
    :param project_id: 需要上传的文件的项目ID
    :param dir_path: 需要上传的路径
    :param user_meta: 需要添加的metadata
    :param current_path: BGIonline上的项目路径
    :return:
    """
    try:
        # print("Createing folder %s ..." % dir_path)
        data = {
            'currentPath': (to_zhcn(current_path or get_fully_path("", False))).encode('utf-8'),
            'path': (to_zhcn(os.path.basename(dir_path))).encode('utf-8'),
            'parents': True
        }
        res = bgionline.api.new_folder(project_id, input_params=data)
        parent_id = res.get("id")
        # print("Done.")
    except Exception as e:
        print("Create folder %s failed. %s " % (dir_path, str(e)))
        return
    # In this scene, os.listdir is better than os.walk
    # for file_path in [os.path.join(dir_path, f) for f in os.listdir(dir_path)] :
    for f in os.listdir(dir_path):
        file_path = os.path.join(dir_path, f)

        # add record
        # if not os.path.getsize(file_path) :
        #    print("File %s size is 0, skip it." % file_path)
        #    continue

        if os.path.isdir(file_path):
            if not os.path.islink(file_path):
                # 拼接BGIonline上的文件夹路径
                if data['currentPath'] is not '/':
                    parent_dir = data['currentPath'] + '/' + os.path.basename(dir_path)
                else:
                    parent_dir = data['currentPath'] + os.path.basename(dir_path)

                upload_directory(upload_record_dict, upload_record_f, lock, metadata, metadatafile_dist, queue,
                                 project_id, file_path, user_meta, parent_dir, wildcard)
        else:
            if wildcard is not None and not fnmatch.fnmatch(os.path.basename(file_path), wildcard):
                continue
            if queue is None:
                try:
                    print ('upload ' + file_path + '...')
                    upload_file(upload_record_dict, upload_record_f, lock, project_id,
                                parent_id, file_path, metadata, metadatafile_dist, show_progres=progres)
                    print (' ')
                except Exception as e:
                    print (e)
            else:
                try:
                    q_data = {
                        'project_id': project_id,
                        'parent_id': parent_id,
                        'f_path': file_path,
                        'user_meta': user_meta,
                        'metadatafile_dist': metadatafile_dist
                    }
                    # print q_data
                    queue.put(q_data)
                except Exception as e:
                    print (e)
                    print("Upload file %s failed." % file_path)


class ProgressPercentage(object):
    def __init__(self, filename, is_concurrent):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()
        self.time = time.time()
        self.is_concurrent = is_concurrent

    def __call__(self, bytes_amount):
        # To simplify we'll assume this is hooked up
        # to a single filename.
        with self._lock:
            self._seen_so_far += bytes_amount
            new_time = time.time()
            percentage = (self._seen_so_far / self._size) * 100
            if self.is_concurrent:
                if OSTYPE == 'windows':
                    global MULTIPROCESSING_CONSUMED
                    global LAST_PERCENT
                    MULTIPROCESSING_CONSUMED.value += (self._seen_so_far - LAST_PERCENT)
                    LAST_PERCENT = self._seen_so_far
                else:
                    global FILE_NAME
                    WRITER.write("[%s%s]    %s    %s\r" % (
                        '=' * int(percentage / 2), (' ' * (50 - int(percentage / 2))),
                        '%4.1f' % percentage + ' %', FILE_NAME))
            else:
                # sys.stdout.write(
                #     "\r%s  %s / %s  (%.2f%%)" % (os.path.basename(self._filename), self._seen_so_far,
                #                                  self._size, percentage))
                if new_time - self.time > 0:
                    sys.stdout.write(" [%s%s]    %s/s\r" % (
                        '=' * int(percentage / 2), (' ' * (50 - int(percentage / 2))),
                        parse_size((bytes_amount / (new_time - self.time)))))
                    self.time = new_time
                    sys.stdout.flush()


class ReadFileChunk(object):
    def __init__(self, fileobj, start_byte, chunk_size, full_file_size,
                 callback=None, enable_callback=True):
        """

        Given a file object shown below:

            |___________________________________________________|
            0          |                 |                 full_file_size
                       |----chunk_size---|
                 start_byte

        :type fileobj: file
        :param fileobj: File like object

        :type start_byte: int
        :param start_byte: The first byte from which to start reading.

        :type chunk_size: int
        :param chunk_size: The max chunk size to read.  Trying to read
            pass the end of the chunk size will behave like you've
            reached the end of the file.

        :type full_file_size: int
        :param full_file_size: The entire content length associated
            with ``fileobj``.

        :type callback: function(amount_read)
        :param callback: Called whenever data is read from this object.

        """
        self._fileobj = fileobj
        self._start_byte = start_byte
        self._size = self._calculate_file_size(
            self._fileobj, requested_size=chunk_size,
            start_byte=start_byte, actual_file_size=full_file_size)
        self._fileobj.seek(self._start_byte)
        self._amount_read = 0
        self._callback = callback
        self._callback_enabled = enable_callback

    @classmethod
    def from_filename(cls, filename, start_byte, chunk_size, callback=None,
                      enable_callback=True):
        """Convenience factory function to create from a filename.

        :type start_byte: int
        :param start_byte: The first byte from which to start reading.

        :type chunk_size: int
        :param chunk_size: The max chunk size to read.  Trying to read
            pass the end of the chunk size will behave like you've
            reached the end of the file.

        :type full_file_size: int
        :param full_file_size: The entire content length associated
            with ``fileobj``.

        :type callback: function(amount_read)
        :param callback: Called whenever data is read from this object.

        :type enable_callback: bool
        :param enable_callback: Indicate whether to invoke callback
            during read() calls.

        :rtype: ``ReadFileChunk``
        :return: A new instance of ``ReadFileChunk``

        """
        f = open(filename, 'rb')
        file_size = os.fstat(f.fileno()).st_size
        return cls(f, start_byte, chunk_size, file_size, callback,
                   enable_callback)

    def _calculate_file_size(self, fileobj, requested_size, start_byte,
                             actual_file_size):
        max_chunk_size = actual_file_size - start_byte
        return min(max_chunk_size, requested_size)

    def read(self, amount=None):
        if amount is None:
            amount_to_read = self._size - self._amount_read
        else:
            amount_to_read = min(self._size - self._amount_read, amount)
        data = self._fileobj.read(amount_to_read)
        self._amount_read += len(data)
        if self._callback is not None and self._callback_enabled:
            self._callback(len(data))
        return data

    def enable_callback(self):
        self._callback_enabled = True

    def disable_callback(self):
        self._callback_enabled = False

    def seek(self, where):
        self._fileobj.seek(self._start_byte + where)
        if self._callback is not None and self._callback_enabled:
            # To also rewind the callback() for an accurate progress report
            self._callback(where - self._amount_read)
        self._amount_read = where

    def close(self):
        self._fileobj.close()

    def tell(self):
        return self._amount_read

    def __len__(self):
        # __len__ is defined because requests will try to determine the length
        # of the stream to set a content length.  In the normal case
        # of the file it will just stat the file, but we need to change that
        # behavior.  By providing a __len__, requests will use that instead
        # of stat'ing the file.
        return self._size

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    def __iter__(self):
        # This is a workaround for http://bugs.python.org/issue17575
        # Basically httplib will try to iterate over the contents, even
        # if its a file like object.  This wasn't noticed because we've
        # already exhausted the stream so iterating over the file immediately
        # stops, which is what we're simulating here.
        return iter([])


client = ''
START_TIME = time.time()


def s3_upload(file_path, remote_path, is_concurrent):
    global START_TIME
    global client

    bucket_name, key_name = remote_path.split("//")[-1].split("/", 1)
    credentials = get_sts_token(True)
    access_key_id = credentials['AccessKeyId']
    access_key_secret = credentials['AccessKeySecret']
    security_token = credentials['STS_Token']
    client = boto3.client('s3',
                          aws_access_key_id=access_key_id,
                          aws_secret_access_key=access_key_secret,
                          aws_session_token=security_token)

    def upload_chunk(part_info, mpu, filepath, q, last_mun, callback, thread_lock, file_record):
        global START_TIME
        global client

        try:
            while (not q.empty()):
                chunk = q.get()
                need_upload = True
                for i in part_info['Parts']:
                    if i['PartNumber'] == chunk.num:
                        need_upload = False
                        with ReadFileChunk.from_filename(filepath, chunk.offset,
                                                         chunk.len, callback) as body:
                            ReadFileChunk.read(body)
                            #ReadFileChunk.enable_callback()
                        break

                if need_upload:
                    with ReadFileChunk.from_filename(filepath, chunk.offset,
                                                     chunk.len, callback) as body:
                        while True:
                            try:
                                if time.time() - START_TIME > 900:
                                    credentials = get_sts_token(True)
                                    access_key_id = credentials['AccessKeyId']
                                    access_key_secret = credentials['AccessKeySecret']
                                    security_token = credentials['STS_Token']
                                    client = boto3.client('s3',
                                                          aws_access_key_id=access_key_id,
                                                          aws_secret_access_key=access_key_secret,
                                                          aws_session_token=security_token)
                                response = client.upload_part(Bucket=bucket_name,
                                                              Key=key_name, PartNumber=chunk.num,
                                                              UploadId=mpu["UploadId"], Body=body)  # step2.上传分片 #可改用多线程
                                part_info['Parts'].append({
                                    'PartNumber': chunk.num,
                                    'ETag': response['ETag']
                                })
                                with thread_lock:
                                    with open(file_record, 'w') as f:
                                        try:
                                            json.dump(part_info.copy(), f)
                                        except Exception as e:
                                            pass
                                break
                            except Exception as e:
                                print ("s3_error:   %s" % e)
                                time.sleep(5)
                    q.task_done()
        except Exception as e:
            print e

    # 结束多线程
    def thread_quit(signum, frame):
        print
        # print 'You choose to stop.'
        sys.exit()

    def upload_file_multipart(filepath, callback, threadcnt):
        global START_TIME
        global client

        part_info = {
            'Parts': []
        }
        filesize = os.stat(filepath).st_size

        q = init_queue(filesize)
        threads = []
        last_mun = q.qsize()
        file_record = bgionline.config.user_config_dir + os.sep + 's3_' + del_punctuation(file_path) + '.record'
        # 断点续传文件准备
        if os.path.isfile(file_record):
            try:
                is_continue = True
                if is_continue:
                    if OSTYPE == 'windows':
                        import io
                        with io.open(file_record, 'r', encoding='windows-1252') as f:
                            part_info = json.load(f)
                    else:
                        with open(file_record, 'r') as f:
                            part_info = json.load(f)
            except Exception as e:
                pass
        thread_lock = threading.Lock()
        if part_info.has_key('mpu'):
            mpu = part_info['mpu']
        else:
            mpu = client.create_multipart_upload(Bucket=bucket_name, Key=key_name)  # step1.初始化
            part_info['mpu'] = mpu

        try:
            signal.signal(signal.SIGINT, thread_quit)
            signal.signal(signal.SIGTERM, thread_quit)
            for i in range(0, threadcnt):
                t = threading.Thread(target=upload_chunk,
                                     args=(part_info, mpu, filepath, q, last_mun, callback, thread_lock, file_record))
                t.setDaemon(True)
                threads.append(t)
                t.start()
            while 1:
                alive = False
                for i in range(0, threadcnt):
                    alive = alive or threads[i].isAlive()
                if not alive:
                    break
        except KeyboardInterrupt, exc:
            print exc
        # q.join()

        part_info_copy = {
            'Parts': []
        }
        for i in range(len(part_info['Parts'])):
            for j in part_info['Parts']:
                if j['PartNumber'] == i + 1:
                    part_info_copy['Parts'].append(j)

        while 1:
            try:
                if time.time() - START_TIME > 900:
                    credentials = get_sts_token(True)
                    access_key_id = credentials['AccessKeyId']
                    access_key_secret = credentials['AccessKeySecret']
                    security_token = credentials['STS_Token']
                    client = boto3.client('s3',
                                          aws_access_key_id=access_key_id,
                                          aws_secret_access_key=access_key_secret,
                                          aws_session_token=security_token)
                client.complete_multipart_upload(Bucket=bucket_name,
                                                 Key=key_name,
                                                 UploadId=mpu["UploadId"], MultipartUpload=part_info_copy)  # step3.完成上传
                if os.path.exists(file_record):
                    os.remove(file_record)
                break
            except:
                pass

    upload_file_multipart(file_path, ProgressPercentage(file_path, is_concurrent), 2)
