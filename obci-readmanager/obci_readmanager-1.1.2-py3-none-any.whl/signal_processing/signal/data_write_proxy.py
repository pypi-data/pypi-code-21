# -*- coding: utf-8 -*-
# Copyright (c) 2016-2018 Braintech Sp. z o.o. [Ltd.] <http://www.braintech.pl>
# All rights reserved.

"""
Module defines single :method 'get_proxy'.

Author:
    Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
"""
from .data_ascii_write_proxy import DataAsciiWriteProxy
from .data_buffered_write_proxy import DataBufferedWriteProxy
from .data_raw_write_proxy import DataRawWriteProxy
from . import signal_logging as logger

LOGGER = logger.get_logger('data_write_proxy', 'info')


def get_proxy(file_path, append_ts=False, use_own_buffer=False, format='FLOAT'):
    """
    Return data write proxy.

    :param file_path: name of file containing data samples
    :param append_ts: append sample timestamp
    :param use_own_buffer: if False create buffer: DataRawWriteProxy else: pass own buffer
    :param format: data format
    :return: proxy or DataAsciiWriteProxy(file_path)
    """
    if format.lower() == 'ascii':
        return DataAsciiWriteProxy(file_path)
    cls = DataBufferedWriteProxy if use_own_buffer else DataRawWriteProxy
    proxy = cls(file_path, append_ts, format)
    return proxy
