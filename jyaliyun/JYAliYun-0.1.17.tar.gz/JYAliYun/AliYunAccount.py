#! /usr/bin/env python
# coding: utf-8

from JYAliYun.Tools import ConfigManager

__author__ = 'ZhouHeng'


class RAMAccount(object):
    """
    配置文件格式
    [Account]
    access_key_id: LTAI***3vAqE****
    access_key_secret: 25QTaQVEQPx***jJolgKuspzPk7***
    internal: false  #  是否为阿里内网
    """

    def __init__(self, conf_path=None, conf_dir=None, conf_name=None, section="Account"):
        self.cfg = ConfigManager(conf_path=conf_path, conf_dir=conf_dir, conf_name=conf_name, section=section)
        self.access_key_id = self.cfg.get("access_key_id")
        self.access_key_secret = self.cfg.get("access_key_secret")
        if self.cfg.has_option("internal") is True:
            self.is_internal = self.cfg.getboolean("internal")
        else:
            self.is_internal = False

    def assign_account_info(self, obj):
        if hasattr(obj, "access_key_id"):
            obj.access_key_id = self.access_key_id
        if hasattr(obj, "access_key_secret"):
            obj.access_key_secret = self.access_key_secret
        if hasattr(obj, "is_internal"):
            obj.is_internal = self.is_internal
