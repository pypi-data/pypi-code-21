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
File transfer functionality
"""
from __future__ import print_function
from builtins import range
from conditional import conditional
from contextlib import closing
from datetime import datetime
import itertools
import json
import logging
import math
import os
import queue
import requests
import sys
import threading
from ncloud.config import SSL_CERT_VERIFICATION

from ncloud.config import \
    (NUM_THREADS, VOLUMES, MULTIPART_UPLOADS, UPLOAD_QUEUE_SIZE)
from ncloud.util.sys_commands import create_all_dirs

logger = logging.getLogger()


class FailedCountException(Exception):
    """if we fail to upload a file, throw this"""

    def __init__(self, count):
        super(FailedCountException, self).__init__()
        self.count = count


def maybe_upload_big_file(config, dataset_id, filepath, filename,
                          batch_size, thread_data, upload_queue):
    file_size = os.path.getsize(filepath)
    if file_size >= batch_size:
        # put the batch files back in the queue to be uploaded
        # by a different thread
        map(upload_queue.put, thread_data.files_to_batch)
        # clear out the files from this thread so it doesn't double upload
        thread_data.files_to_batch = set()
        upload_big_file(
            config, dataset_id, filename, filepath, batch_size)
        thread_data.files_uploaded += 1
        return True
    return False


def batch_upload_if_empty_queue(config, dataset_id, upload_queue, thread_data):
    if upload_queue.empty():
        # if the queue is empty, upload any files if they are still batched
        if thread_data.files_to_batch:
            if dataset_id:
                upload_batch(config, thread_data.files_to_batch, dataset_id)
                thread_data.files_uploaded += len(thread_data.files_to_batch)
            else:
                # if the threads got through the queue fast enough that we
                # haven't set the upload queue's dataset id yet, then
                # put all files back in the queue
                map(upload_queue.put, thread_data.files_to_batch)
        return True
    return False


def process_batch(config, batch_size, thread_data, upload_queue,
                  processed_file=None, filepath=None, filename=None):
    if filepath and processed_file:
        raise ValueError(
            "Unable to process dataset upload. Please report.", 500)
    if processed_file:
        _, file_data = processed_file
        file_size = os.fstat(file_data[1].fileno()).st_size
    else:
        file_size = os.path.getsize(filepath)
        file_data = (filename, open(filepath, 'rb'))
    # either add to the batch or upload what we've got
    if thread_data.current_batch_size < batch_size:
        thread_data.files_to_batch.add(('files', file_data))
        thread_data.current_batch_size += file_size

    if thread_data.current_batch_size >= batch_size:
        upload_batch(config, thread_data.files_to_batch,
                     thread_data.dataset_id)


def upload_files(config, volume_id, upload_queue, batch_size, thread_data):
    """Each thread will upload at least one file if able
       If a thread encounters a large file bigger than batch size
       then it will put the current files list back in the queue and upload
       the big file and return, which avoids blocking the smaller files
       from being uploaded. If thread encounters a file that would exceed
       the batch size, it will upload the current batch and put the current
       file back in the queue.
    """
    thread_data.files_uploaded = 0
    thread_data.current_batch_size = 0
    thread_data.files_to_batch = set()
    # assuming here that all files go to same dataset, as that's how
    # the ncloud upload works now
    thread_data.dataset_id = volume_id
    try:
        while thread_data.current_batch_size < batch_size:
            try:
                file_tuple = upload_queue.get_nowait()
            except queue.Empty:
                # make sure this thread doesn't still have things to upload
                batch_upload_if_empty_queue(
                    config, thread_data.dataset_id, upload_queue, thread_data)
                break
            # if we've already seen this file, size will be two
            # and we know the file won't be large
            if len(file_tuple) == 2:
                thread_data.processed_file = file_tuple
                process_batch(config, batch_size, thread_data, upload_queue,
                              processed_file=thread_data.processed_file)
            else:
                (dataset_id, filename, filepath) = file_tuple
                upload_queue.dataset_id = dataset_id
                large_file = maybe_upload_big_file(
                    config, dataset_id, filepath, filename, batch_size,
                    thread_data, upload_queue)
                if not large_file:
                    process_batch(
                        config, batch_size, thread_data, upload_queue,
                        filepath=filepath, filename=filename)
            empty = batch_upload_if_empty_queue(
                config, upload_queue.dataset_id, upload_queue, thread_data)
            if empty:
                break
    except (SystemExit, Exception):
        # want to return the number of files attempted at uploading
        raise FailedCountException(len(thread_data.files_to_batch))
    finally:
        upload_queue.task_done()

    return thread_data.files_uploaded


def upload_batch(config, files, dataset_id):
    # TODO: restructure
    from ncloud.commands.command import Command
    return Command.api_call(
        config, VOLUMES + dataset_id, method="POST", files=files,
        hide_output=False)


def upload_big_file(config, dataset_id, filename, filepath, batch_size):
    # TODO: restructure
    from ncloud.commands.command import Command
    vals = {'multipart': True, 'filename': filename}
    res = Command.api_call(config, VOLUMES + dataset_id, method="POST",
                           data=vals, return_json=True, hide_output=False)
    return multipart_upload(config, filepath, res['multipart_id'],
                            batch_size, output=False)


def parallel_upload(config, path, volume_id, upload_queue, batch_size,
                    follow_symlinks):
    def upload_thread():
        while not upload_queue.empty():
            try:
                files_uploaded = upload_files(
                    config, volume_id, upload_queue, batch_size, thread_data)
                if files_uploaded == 0:
                    continue
                lock.acquire()
                upload_thread.success += int(files_uploaded)
            except FailedCountException as e:
                lock.acquire()
                upload_thread.failed += e.count
            finally:
                print(("\r{}/{} Uploaded. {} Failed.".format(
                    upload_thread.success, total_files, upload_thread.failed)
                ), end=' '
                )
                sys.stdout.flush()
                try:
                    lock.release()
                except RuntimeError:
                    # if a thread continued in the loop without ever acquiring
                    # a lock
                    pass

    def upload_thread_helper(total_files):
        for t in range(NUM_THREADS):
            thread = threading.Thread(target=upload_thread)
            thread.daemon = True
            thread.start()
            threads.append(thread)

        for t in threads:
            t.join()

    def walk_generator():
        return os.walk(path, followlinks=follow_symlinks)

    #  Organize items of iterable to groups of size n
    def grouper(n, iterable):
        it = iter(iterable)
        while True:
            group = list(itertools.islice(it, n))
            if not group:
                return
            yield group

    lock = threading.RLock()
    thread_data = threading.local()
    upload_thread.success = 0
    upload_thread.failed = 0
    total_files = 0
    threads = []

    if os.path.isdir(path):  # directory upload
        total_files = len([f for _, _, filelist in walk_generator()
                           for f in filelist if f[0] != '.'])
        for dirpath, _, filenames in walk_generator():
            filenames = [f for f in filenames if f[0] != '.']
            reldir = os.path.relpath(dirpath, path)
            reldir = reldir if reldir != "." else ""
            for files_group in grouper(n=UPLOAD_QUEUE_SIZE,
                                       iterable=filenames):
                for filename in files_group:
                    relfile = os.path.join(reldir, filename)
                    filepath = os.path.join(path, relfile)
                    upload_queue.put((volume_id, relfile, filepath))
                    if upload_queue.full():
                        upload_thread_helper(total_files)
        # upload remaining items on the queue
        if not upload_queue.empty():
            upload_thread_helper(total_files)
    else:  # single file upload
        total_files = 1
        filename = os.path.basename(path)
        filepath = path  # makes the code more readable
        upload_queue.put((volume_id, filename, filepath))
        upload_thread_helper(total_files)
    print()
    return upload_thread.success, upload_thread.failed, total_files


def multipart_upload(config, input, multipart_id,
                     chunksize=5242880, output=True):
    # TODO: restructure
    from ncloud.commands.command import Command
    multipart_url = MULTIPART_UPLOADS + str(multipart_id)
    basename = os.path.basename(input)
    file_size = os.path.getsize(input)

    num_chunks = int(math.ceil(float(file_size) / chunksize))
    with open(input, "rb") as model:
        if output:
            print(("\r0/{} Parts of {} Uploaded".format(
                num_chunks, basename)), end=' ')
        sys.stdout.flush()

        part_num = 0
        chunk = model.read(chunksize)
        parts = []
        while chunk != "" and len(chunk) != 0:
            part_num += 1
            vals = {'part_num': part_num}
            files = [('part', (basename, chunk))]
            res = Command.api_call(config, multipart_url, method="POST",
                                   data=vals, files=files, return_json=True)
            parts.append({"ETag": res["ETag"], "PartNumber": part_num})
            chunk = model.read(chunksize)
            if output:
                print(("\r{}/{} Parts of {} Uploaded".format(
                    part_num, num_chunks, basename)), end=' ')
            sys.stdout.flush()

        if output:
            print("")
        return Command.api_call(
            config,
            multipart_url + "/complete",
            method="POST",
            data=json.dumps(parts),
            headers={"Content-Type": "application/json"},
            return_json=True
        )


def download_file(filename, stream, download_url=None, download_request=None):
    if (download_url and download_request) or \
            not (download_url or download_request):
        raise ValueError(
            'Either download from file or from request.', 500)

    with conditional(download_url, closing(download_url)) as obj:
        with open(filename, 'wb') as f:
            # |= doesn't work here O_o
            obj = (obj or download_request)
            if stream:
                for chunk in obj.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            else:
                f.write(obj)


def download_objects(results, directory):
    """results is a dict containing "result_list"
       each result contains a "filename" and "url" to request
    """
    for result in results["result_list"]:
        filename = os.path.join(directory, result["filename"])
        create_all_dirs(filename)
        download_file(
            filename, stream=True,
            download_url=requests.get(result["url"], stream=True,
                                      verify=SSL_CERT_VERIFICATION))


def download_compressed(results, directory, object_id, ext, stream):
    """results: an api call to our server
       directory: where the results will be downloaded to
       object_id: which object to download results for
       ext: "zip" or "tar"
       stream: only supported with "tar"; chunks the download
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = (
        'results_%s_%s.%s' % (
            object_id,
            datetime.strftime(datetime.today(), "%Y%m%d%H%M%S"),
            ext
        )
    )
    filename = os.path.join(directory, filename)
    download_file(filename, stream=stream, download_request=results)

    return filename
