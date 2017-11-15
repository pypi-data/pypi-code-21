#!/usr/bin/python2
# encoding=utf-8
import os
import time
import requests


def download(url, filename, callback=None, force=False, headers={}, check_length=False):
    start = time.time()
    if not force and os.path.exists(filename) and os.path.getsize(filename) > 0:
        return (True, filename, time.time() - start)
    filepath = os.path.dirname(os.path.abspath(filename))
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    temp_filename = filename + ".tmp"
    try:
        res = requests.get(url, headers=headers, stream=True, timeout=60)
        if res.status_code != 200:
            return (False, "HTTP code {0}".format(res.status_code), time.time() - start)
        f = open(temp_filename, "wb")
        length = int(res.headers.get("content-length", 0))
        buflen = 4096
        count = 0
        for chunk in res.iter_content(buflen):
            count += len(chunk)
            f.write(chunk)
            if callback:
                callback(count, length, time.time() - start)
        f.close()
        if check_length and count != length:
            return (False, "content-length not equal", time.time() - start)
        os.rename(temp_filename, filename)
        return (True, filename, time.time() - start)
    except Exception as e:
        return (False, str(e), time.time() - start)
    finally:
        try:
            f.close()
            res.close()
        except Exception:
            pass


def upload(filename, url, callback=None, **kwargs):
    class IterableToFileAdapter(object):
        def __init__(self, iterable):
            self.iterator = iter(iterable)
            self.length = iterable.total

        def read(self, size=-1):
            return next(self.iterator, b'')

        def __len__(self):
            return self.length

    import poster
    from collections import OrderedDict

    start = time.time()
    if not os.path.exists(filename):
        return (False, "File not exists.", time.time() - start)

    data = OrderedDict(**kwargs)
    files = None
    headers = None

    def real_callback(p, current, total):
        if not callback:
            return
        callback(current, total, time.time() - start)

    if not callback:
        files = {'files': open(filename, 'rb')}
    else:
        data["files"] = open(filename, 'rb')
        datagen, headers = poster.encode.multipart_encode(
            params=data, cb=real_callback)
        data = IterableToFileAdapter(datagen)

    try:
        res = requests.post(url,
                            data=data,
                            headers=headers,
                            files=files,
                            timeout=60)
        success = False
        if res.status_code == 200:
            success = True
        return (success, res.text.strip(), time.time() - start)
    except Exception as e:
        return (False, e, time.time() - start)
