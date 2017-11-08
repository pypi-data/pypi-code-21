#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/11/7
 """
from __future__ import unicode_literals, absolute_import
from djdg_core.common_api.public import common_client


def file_upload(file_info):
    """
    上传文件
    :param file_info: (filename, file_obj[, mime_type])
    :return:
    """
    res = common_client.get_resource('upload', app='file')
    form_data = {
        'uploadedFile': file_info
    }
    # ret = res.do_request(method='post', action=common_client.oauth_app_id, multi_part_fields=form_data, end_slash=False)
    ret = res.do_request(method='post', multi_part_fields=form_data, end_slash=False)
    return ret.data
