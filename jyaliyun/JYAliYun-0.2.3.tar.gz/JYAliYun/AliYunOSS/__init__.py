#! /usr/bin/env python
# coding: utf-8

import os
from time import time
from lxml import etree
from urllib import quote
from JYAliYun import AliYUN_DOMAIN_NAME
from JYAliYun.AliYunObject import ObjectManager
from JYAliYun.Tools import ali_signature, jy_requests

__author__ = 'meisanggou'


class OssObject(object):
    @staticmethod
    def format_key(key):
        if not key.startswith("/"):
            return "/" + key
        return key

    @staticmethod
    def get_resource(oss_object, sub_resource=None):
        if isinstance(sub_resource, dict):
            sub_rs = []
            for key in sorted(sub_resource.keys()):
                if sub_resource[key] is None:
                    sub_rs.append(key)
                else:
                    sub_rs.append("%s=%s" % (key, sub_resource[key]))
            if len(sub_rs) > 0 and len(oss_object) > 1:
                oss_object += "?" + "&".join(sub_rs)
        return oss_object

    def __init__(self, bucket_name, key, sub_key=None):
        self.bucket_name = bucket_name
        self.key = self.format_key(key)
        self.resource = self.get_resource(self.key, sub_key)
        self.full_resource = "/%s%s" % (self.bucket_name, self.resource)


class OSSBucket(ObjectManager):
    PRODUCT = "OSS"

    def __init__(self, *args, **kwargs):
        if "default_section" not in kwargs:
            kwargs["default_section"] = "OSS"
        super(OSSBucket, self).__init__(*args, **kwargs)

        if self.cfg.get("bucket") is not None:
            self.bucket_name = self.cfg.get('bucket')
        if "bucket_name" in kwargs:
            self.bucket_name = kwargs["bucket_name"]
        if self.bucket_name.lower() == "local":
            self.is_local = True
        else:
            self.is_local = False
        self.region = self.cfg.get("region", "beijing")
        self.protocol = self.cfg.get("protocol", "http")
        if self.is_internal is True:
            self.endpoint = "oss-cn-%s-internal.%s" % (self.region, AliYUN_DOMAIN_NAME)
        else:
            self.endpoint = "oss-cn-%s.%s" % (self.region, AliYUN_DOMAIN_NAME)
        self.server_url = "%s.%s" % (self.bucket_name, self.endpoint)

    @staticmethod
    def get_resource(bucket_name, oss_object, sub_resource=None):
        oss_object = OSSBucket.format_key(oss_object)
        if isinstance(sub_resource, dict):
            sub_rs = []
            for key in sorted(sub_resource.keys()):
                if sub_resource[key] is None:
                    sub_rs.append(key)
                else:
                    sub_rs.append("%s=%s" % (key, sub_resource[key]))
            if len(sub_rs) > 0:
                oss_object += "?" + "&".join(sub_rs)
        return "/%s/%s" % (bucket_name, oss_object)

    @staticmethod
    def format_key(key):
        return key.lstrip("/")

    def join_url(self, oss_object, server_url=None):
        url = self.protocol + "://"
        if server_url is not None:
            url += server_url
        else:
            url += self.server_url
        if oss_object.startswith("/"):
            oss_object = oss_object[1:]
        url += "/" + quote(oss_object, '')
        return url

    def sign_file_url(self, key, method="GET", expires=60, server_url=None):
        if self.is_local is True:
            return None
        key = OSSBucket.format_key(key)
        sign_url = self.join_url(key, server_url)
        expires = "%s" % int(time() + expires)
        resource_string = self.get_resource(self.bucket_name, key)
        signature = ali_signature(self.access_key_secret, method, "", "", expires, "", resource_string)
        sign_url += "?OSSAccessKeyId=%s&Expires=%s&Signature=%s" % (self.access_key_id, expires, quote(signature, ""))
        return sign_url

    def head_object(self, object_key):
        if self.is_local is True:
            resp = jy_requests.JYResponse()
            if os.path.exists(object_key) is False:
                resp.status_code = 404
                return resp
            resp.headers["Content-Length"] = os.path.getsize(object_key)
            return resp
        oss_object = OssObject(self.bucket_name, object_key)
        url = self.join_url(oss_object.resource)
        headers = self.ali_headers("HEAD", oss_object.full_resource)
        response = jy_requests.head(url, headers=headers)
        return response

    def init_mul_upload(self, object_key):
        oss_object = OssObject(self.bucket_name, object_key, {"uploads": None})
        headers = self.ali_headers("POST", oss_object.full_resource)
        url = self.join_url(oss_object.resource)
        r_d = jy_requests.post(url, headers=headers)
        if r_d.status_code / 100 != 2:
            return r_d
        res_ele = etree.fromstring(r_d.text.encode("utf-8"))
        r_d["data"] = dict(bucket_name=res_ele.find("Bucket").text, key=res_ele.find("Key").text,
                           upload_id=res_ele.find("UploadId").text)
        return r_d

    def part_copy(self, upload_id, part_num, object_key, copy_range, source_object, source_bucket=None):
        if source_bucket is None:
            source_bucket = self.bucket_name
        copy_source = OSSBucket.get_resource(source_bucket, source_object)
        x_headers = {"x-oss-copy-source": copy_source, "x-oss-copy-source-range": copy_range}
        del x_headers["x-oss-copy-source-range"]

        sub_resource = dict(partNumber=part_num, uploadId=upload_id)
        oss_object = OssObject(self.bucket_name, object_key, sub_resource)
        headers = self.ali_headers("PUT", oss_object.full_resource, headers=x_headers)
        url = self.join_url(oss_object.resource)
        r_d = jy_requests.put(url, params=sub_resource, headers=headers)
        return r_d

    def list_object(self, delimiter=None, marker=None, max_keys=100, prefix=None):
        sub_resource = dict()
        if delimiter is not None:
            sub_resource["delimiter"] = delimiter
        if marker is not None:
            sub_resource["marker"] = marker
        if isinstance(max_keys, int):
            sub_resource["max-keys"] = max_keys
        if prefix is not None:
            sub_resource["prefix"] = prefix
        oss_object = OssObject(self.bucket_name, "", sub_resource)
        headers = self.ali_headers("GET", oss_object.full_resource)
        url = self.join_url(oss_object.resource)
        r_d = jy_requests.get(url, params=sub_resource, headers=headers)
        if r_d.status_code / 100 != 2:
            return r_d
        res_ele = etree.fromstring(r_d.text.encode("utf-8"))
        object_list = []
        for item_content in res_ele.findall("Contents"):
            object_meta = {"key": item_content.find("Key").text, "size": long(item_content.find("Size").text)}
            object_list.append(object_meta)
        for item_content in res_ele.findall("CommonPrefixes"):
            object_meta = {"key": item_content.find("Prefix").text, "size": 0}
            object_list.append(object_meta)
        is_truncated = res_ele.find("IsTruncated").text
        r_d.data = dict(is_truncated=is_truncated, keys=object_list)
        if is_truncated == "true":
            next_marker = res_ele.find("NextMarker").text
            r_d.data.update(next_marker=next_marker)
        return r_d

    def list_all_object(self, prefix=None):
        object_list = []
        next_marker = None
        while True:
            r_d = self.list_object(prefix=prefix, marker=next_marker, max_keys=999)
            if r_d.status_code / 100 != 2:
                return r_d
            object_list.extend(r_d.data["keys"])
            if "next_marker" not in r_d.data:
                r_d.data["keys"] = object_list
                return r_d
            next_marker = r_d.data["next_marker"]
        return None


if __name__ == "__main__":
    from JYAliYun.AliYunAccount import RAMAccount
    # oss_account = RAMAccount(conf_path="/data/Web2/conf/oss.conf")
    s = OSSBucket(conf_path="/data/Web2/conf/oss.conf")
    print s.head_object("/data/Web2/conf/oss.conf")