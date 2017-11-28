#! /usr/bin/env python
# coding: utf-8

from JYAliYun import AliYUN_DOMAIN_NAME
from JYAliYun.AliYunObject import ObjectManager
from JYAliYun.AliYunMNS.AliMNSTopics import MNSTopicsManager

__author__ = 'ZhouHeng'


class MNSServerManager(ObjectManager):
    """
    配置文件格式
    [MNS]
    account_id: 1530531001163833
    region: beijing
    """
    PRODUCT = "MNS"

    def __init__(self, *args, **kwargs):
        kwargs.update(default_section="MNS", default_conf_name="mns.conf", disabled_log=True)
        super(MNSServerManager, self).__init__(*args, **kwargs)
        self.account_id = self.cfg.get("account_id")
        if self.account_id is None:
            self.account_id = kwargs["account_id"]
        self.region = self.cfg.get("region")
        if self.region is None:
            self.region = kwargs["region"]

    def get_server_url(self):
        if self.server_url is not None:
            return self.server_url
        if self.is_internal is True:
            protocol = "http"
            region_ext = "-internal"
        else:
            protocol = "http"
            region_ext = ""
        self.server_url = "%s://%s.mns.cn-%s%s.%s" % (protocol, self.account_id, self.region, region_ext,
                                                      AliYUN_DOMAIN_NAME)
        return self.server_url

    def get_topic(self, topic_name):
        mns_topic = MNSTopicsManager(topic_name, ram_account=self.ram_account, cfg=self.cfg)
        mns_topic.set_server_url(self.get_server_url())
        return mns_topic
