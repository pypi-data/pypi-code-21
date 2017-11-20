# ----------------------------------------------------------------------------
# Copyright 2015-2017 Nervana Systems Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------------------------------------------------------
#
# # -*- coding: utf-8 -*-
"""
Subcommands for managing datasets.
"""
from __future__ import print_function
from builtins import str

import os
from functools import partial
import bson
import threading
import signal
import sys
import time
import queue
from queue import Queue
from hashlib import sha256
from collections import defaultdict

from ncloud.commands.command import Command, build_subparser
from ncloud.commands.command import LS, UL, LN
from ncloud.util.compat import range
from ncloud.config import DATA_OBJECT, DATA_RECORD, DATA_COLLECTION
from ncloud.formatting.output import print_table
from ncloud.completers import DatasetCompleter


NUM_T_INGEST = 1
NUM_T_EXIST = 5
NUM_T_UPLOAD = 5
NUM_T_STATUS = 1

EXIST_CALL_SIZE = 200
UPLOAD_CALL_SIZE = 50
SHA_QUEUE_MAXSIZE = 10000
UPLOAD_QUEUE_MAXSIZE = 0
MULTIPART_QUEUE_MAXSIZE = 0

MAX_FILE_SIZE = 50000

thread_exit = False


class List(Command):
    """
    List available datasets.
    """
    @classmethod
    def parser(cls, subparser):
        dataset_list = subparser.add_parser(LS.name, aliases=LS.aliases,
                                            help=List.__doc__,
                                            description=List.__doc__)
        dataset_list.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config):
        return List.api_call(config, DATA_COLLECTION, return_json=True)

    @staticmethod
    def display_after(config, args, res):
        if res:
            print_table(res['datasets'])


class Upload(Command):
    """
    Upload a custom dataset to Nervana Cloud.
    """
    @classmethod
    def parser(cls, subparser):
        dataset_upload = subparser.add_parser(UL.name, aliases=UL.aliases,
                                              help=Upload.__doc__,
                                              description=Upload.__doc__)
        dataset_upload.add_argument("manifest", help="Manifest file")
        dataset_upload.add_argument("-n", "--name",
                                    help="Colloquial name of the dataset. "
                                         "Default name will be given if not "
                                         "provided.")
        dataset_upload.add_argument(
            "-i", "--dataset-id", default=None, type=str,
            help="Add data to an existing dataset "
                 "with this id. This will replace identically-named files."
        ).completer = DatasetCompleter
        dataset_upload.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, manifest, name=None, dataset_id=None):
        if not os.path.isfile(manifest):
            print('Manifest file {} not found, or is a directory.'.format(
                manifest))
            return

        record_queue = Queue(maxsize=SHA_QUEUE_MAXSIZE)
        upload_queue = Queue(maxsize=UPLOAD_QUEUE_MAXSIZE)
        multipart_queue = Queue(maxsize=MULTIPART_QUEUE_MAXSIZE)
        upload_count, exist_count, record_count, total_count, failure_count, \
            multipart_count, ingest_done, exist_done = Counter(), Counter(), \
            Counter(), Counter(), Counter(), Counter(), Counter(), Counter()

        # create new dataset
        data = {}
        if name:
            data['name'] = name
        res = Upload.api_call(
            config, DATA_COLLECTION, method="POST", data=data,
            return_json=True, hide_output=False)
        dataset_id = res['dataset_id']

        # Start Threads to ingest manifest, check if objects exists, and upload
        global thread_exit
        thread_exit = False

        def thread_exit_signal(signal, frame):
            global thread_exit
            thread_exit = True

        signal.signal(signal.SIGINT, thread_exit_signal)

        threads = []
        threads.extend(init_threads(NUM_T_INGEST, ingest_manifest,
                                    (manifest, record_queue, total_count,
                                     ingest_done, failure_count)))
        threads.extend(init_threads(NUM_T_EXIST, objects_exist,
                                    (config, record_queue, upload_queue,
                                     ingest_done, exist_count, exist_done,)))
        threads.extend(init_threads(NUM_T_UPLOAD, upload_records,
                                    (config, dataset_id, upload_queue,
                                     multipart_queue, exist_done, upload_count,
                                     record_count, multipart_count,)))
        threads.extend(init_threads(NUM_T_STATUS, status,
                                    (upload_count, exist_count, record_count,
                                     total_count, multipart_count,
                                     ingest_done, failure_count)))

        # Wait for all objects to be uploaded
        while threading.active_count() > 1:
            time.sleep(0.1)

        # finalize dataset
        if not thread_exit:
            Upload.api_call(
                config, DATA_COLLECTION, method="POST",
                data={'id': dataset_id, 'finalized': True},
                return_json=True, hide_output=False)

        output = {"id": dataset_id, "num_records": record_count.value()}

        return output

    @staticmethod
    def display_after(config, args, res):
        print_table(res)


def init_threads(num_threads, target, args=()):
    workers = []
    for _ in range(num_threads):
        t = threading.Thread(target=target, args=args)
        t.daemon = True
        t.start()
        workers.append(t)
    return workers


def upload_records(config, dataset_id, upload_queue, multipart_queue,
                   exist_done, upload_count, record_count, multipart_count):
    """
    Upload records (and associated files)
    """
    global thread_exit
    done = False
    while not done and not thread_exit:
        records = []
        files = dict()

        # Populate record list and file dict
        while len(records) < UPLOAD_CALL_SIZE and not done:
            try:
                record = upload_queue.get(block=True, timeout=0.1)
                records.append(record.get_record())
                record_count.increment()
                upload_queue.task_done()
                for data in [record.obj, record.meta]:
                    if not data.exists:
                        with open(data.path) as f:
                            files[data.SHA] = f.read()
                        upload_count.increment()
            except queue.Empty:
                if thread_exit:
                    return
                if exist_done.value() == NUM_T_EXIST:
                    done = True
                    break

        # Upload records
        record_request = {
            'dataset_id': dataset_id,
            'records': records,
            'files': files
        }
        if (len(records) or len(files)) and not thread_exit:
            Upload.api_call(config, DATA_RECORD, method="POST",
                            data=bson.dumps(record_request),
                            return_json=True, hide_output=False)


def objects_exist(config, record_queue, upload_queue, ingest_done,
                  exist_count, exist_done):
    """
    Checks API for pre-existing objects to avoid re-uploading
    """
    global thread_exit
    done = False
    while not done and not thread_exit:
        records = []
        files = defaultdict(list)
        sha_list = []

        while len(records) < EXIST_CALL_SIZE and not done:
            try:
                record = record_queue.get(block=True, timeout=0.1)
                records.append(record)

                files[record.obj.SHA].append(record.obj)
                files[record.meta.SHA].append(record.meta)
                sha_list.append(record.obj.SHA)
                sha_list.append(record.meta.SHA)

                record_queue.task_done()
            except queue.Empty:
                if thread_exit:
                    return
                if ingest_done.value() == NUM_T_INGEST:
                    done = True
                    break

        # Check which SHAs exist
        if len(sha_list):
            res = Upload.api_call(config, DATA_OBJECT + "/exists",
                                  data={'object_shas': sha_list},
                                  return_json=True, hide_output=False)
            for sha in res['exist']:
                data = files[sha]
                for f in data:
                    f.exists = True
                exist_count.increment()

        for record in records:
            put_record = False
            while not put_record:
                try:
                    upload_queue.put(record, timeout=0.1)
                    put_record = True
                except queue.Full:
                    if thread_exit:
                        return

    exist_done.increment()


def get_obj_and_meta_paths(line, manifest):
    manifest_dir_path = os.path.dirname(manifest)
    paths = []
    for path in line.strip('\n').split(','):
        if not os.path.isabs(path):
            # make each path relative to directory of manifest
            # so it doesn't matter where the manifest is located
            # only if not an absolute path
            path = os.path.join(manifest_dir_path, path)
        paths.append(path)
    # temp fix until below is resolved
    if not paths or len(paths) != 2:
        paths = ['bad', 'paths']
    # TODO: report bad manifest files in csv to user
    # see https://jira01.devtools.intel.com/browse/NC3-704
    # if not paths or len(paths) != 2 or not validate_paths(paths):
    #     # make sure that we have both obj and meta path
    #     print("Invalid line in manifest: {}".format(line))
    #     sys.stdout.flush()
    #     thread_exit = True
    return paths


def validate_paths(*paths):
    for path in paths:
        if not os.path.isfile(path):
            return False
    return True


def ingest_manifest(manifest, record_queue, total_count, ingest_done,
                    failure_count):
    """
    Ingests manifest file and populates queue with Records to be uploaded
    """
    global thread_exit
    try:
        with open(manifest) as f:
            while not thread_exit:
                line = f.readline()
                if line == "":
                    break
                obj_path, meta_path = get_obj_and_meta_paths(line, manifest)
                if not validate_paths(obj_path, meta_path):
                    # don't terminate upload process on invalid manifest files
                    total_count.increment()
                    failure_count.increment()
                    continue
                with open(obj_path, 'rb') as obj_file, \
                        open(meta_path, 'rb') as meta_file:
                    obj = Data(compute_sha(obj_file.read()), obj_path)
                    meta = Data(compute_sha(meta_file.read()), meta_path)

                record = Record(obj, meta)
                while record_queue.full():
                    if thread_exit:
                        break
                    else:
                        time.sleep(0.1)

                record_queue.put(record)
                total_count.increment()
        ingest_done.increment()
    except Exception as e:
        print('Exception caught: {}'.format(e))
        # in case we miss anything, we don't want threads to hang
        thread_exit = True


def status(upload_count, exist_count, record_count, total_count,
           multipart_count, ingest_done, failure_count):
    global thread_exit
    while not thread_exit:
        if multipart_count.value() == 0:
            status = "Records Created {}/{} | {} objects uploaded, " \
                     "{} existing objects skipped".format(record_count,
                                                          total_count,
                                                          upload_count,
                                                          exist_count)
        else:
            status = "Records Created {}/{} | {} objects uploaded, " \
                     "{} existing objects skipped | {} objects too large"\
                .format(record_count, total_count, upload_count, exist_count,
                        multipart_count)
        sys.stdout.write('\r')
        sys.stdout.write(status)
        sys.stdout.flush()
        if ingest_done.value() > 0:
            if (record_count.value() + failure_count.value() ==
                    total_count.value()):
                print("\n")
                break
        time.sleep(0.1)


class Counter(object):

    def __init__(self):
        self.count = 0
        self.lock = threading.Lock()

    def increment(self):
        with self.lock:
            self.count += 1

    def decrement(self):
        with self.lock:
            self.count -= 1

    def value(self):
        return self.count

    def __repr__(self):
        return "{}".format(self.count)


class Data:

    def __init__(self, SHA, file_path):
        self.SHA = SHA
        self.path = file_path
        self.size = os.path.getsize(file_path)
        self.link = None
        self.exists = False

    def __repr__(self):
        return "{}: {}".format(self.SHA, self.path)


class Record:

    def __init__(self, obj, meta):
        if not isinstance(obj, Data) or not isinstance(meta, Data):
            raise TypeError("Arguments must be Data objects")
        self.obj = obj
        self.meta = meta
        self.obj.link = meta
        self.meta.link = obj

    def __repr__(self):
        return "Object: {} | Meta: {}".format(self.obj.SHA, self.meta.SHA)

    def get_record(self):
        return tuple((self.obj.SHA, self.meta.SHA))


def compute_sha(object):
    return sha256(object).hexdigest()


class Link(Command):
    """
    Link a dataset not residing in the Nervana Cloud.
    """
    @classmethod
    def parser(cls, subparser):
        dataset_link = subparser.add_parser(LN.name, aliases=LN.aliases,
                                            help=Link.__doc__,
                                            description=Link.__doc__)
        dataset_link.add_argument("manifest", help="Manifest file")
        dataset_link.add_argument("location_path",
                                  help="Network path of the data root "
                                       "directory.")
        dataset_link.add_argument("-n", "--name",
                                  help="Colloquial name of the dataset. "
                                       "Default name will be given if not "
                                       "provided.")
        dataset_link.add_argument("-e", "--region",
                                  help="Region in which dataset resides.  "
                                       "For S3, defaults to us-west-1")

        dataset_link.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, manifest, location_path, name=None, region=None):
        data = {}

        if name is not None:
            data['name'] = name

        if region is not None:
            data["region"] = region

        res = Link.api_call(config, DATA_COLLECTION, method="POST",
                            data=data, return_json=True)
        dataset_id = res['dataset_id']

        files = [('manifest', (os.path.basename(manifest),
                 open(manifest, "rb")))]
        data = {"location_path": location_path, "dataset_id": dataset_id}

        res = Link.api_call(config, DATA_RECORD, method="POST",
                            data=data, files=files, return_json=True)

        return {"dataset_id": dataset_id}

    @staticmethod
    def display_after(config, args, res):
        print_table(res)


parser = partial(
    build_subparser, 'dataset', ['ds', 'd'], __doc__,
    (List, Upload, Link)
)
