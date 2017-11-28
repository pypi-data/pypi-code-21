#! /usr/bin/env python
# coding: utf-8

from JYAliYun.AliYunObject import ObjectManager
from JYAliYun.Tools import jy_requests
from JYAliYun.Tools import get_params

__author__ = 'meisanggou'


class RAMUserManager(ObjectManager):
    PRODUCT = "RAM"
    address = "https://ram.aliyuncs.com"

    def list_users(self):
        action = "ListUsers"
        http_method = "GET"
        custom_params = dict(Action=action)
        params = get_params(self.access_key_id, self.access_key_secret, http_method, custom_params)
        resp = jy_requests.request(http_method, self.address, params=params)
        return resp

    def get_user(self, user_name):
        action = "GetUser"
        http_method = "GET"
        custom_params = dict(Action=action, UserName=user_name)
        params = get_params(self.access_key_id, self.access_key_secret, http_method, custom_params)
        resp = jy_requests.request(http_method, self.address, params=params)
        return resp

    def list_access_keys(self, user_name):
        action = "ListAccessKeys"
        http_method = "GET"
        custom_params = dict(Action=action, UserName=user_name)
        params = get_params(self.access_key_id, self.access_key_secret, http_method, custom_params)
        resp = jy_requests.request(http_method, self.address, params=params)
        return resp

    def create_user(self, user_name, **kwargs):
        action = "CreateUser"
        http_method = "GET"
        custom_params = dict(Action=action, UserName=user_name)
        allow_keys = {"display_name": "DisplayName", "mobile_phone": "MobilePhone", "email": "Email",
                      "comments": "Comments"}
        for key in allow_keys.keys():
            if key in kwargs:
                custom_params[allow_keys[key]] = kwargs[key]
        params = get_params(self.access_key_id, self.access_key_secret, http_method, custom_params)
        resp = jy_requests.request(http_method, self.address, params=params)
        return resp

    def delete_user(self, user_name):
        action = "DeleteUser"
        http_method = "GET"
        custom_params = dict(Action=action, UserName=user_name)
        params = get_params(self.access_key_id, self.access_key_secret, http_method, custom_params)
        resp = jy_requests.request(http_method, self.address, params=params)
        return resp

    def create_access_key(self, user_name):
        action = "CreateAccessKey"
        http_method = "GET"
        custom_params = dict(Action=action, UserName=user_name)
        params = get_params(self.access_key_id, self.access_key_secret, http_method, custom_params)
        resp = jy_requests.request(http_method, self.address, params=params)
        return resp

    def create_policy(self, policy_name, policy_document, description=None):
        action = "CreatePolicy"
        http_method = "GET"
        custom_params = dict(Action=action, PolicyName=policy_name, PolicyDocument=policy_document)
        if description is not None:
            custom_params["Description"] = description
        params = get_params(self.access_key_id, self.access_key_secret, http_method, custom_params)
        resp = jy_requests.request(http_method, self.address, params=params)
        return resp

    def delete_policy(self, policy_name):
        action = "DeletePolicy"
        http_method = "GET"
        custom_params = dict(Action=action, PolicyName=policy_name)
        params = get_params(self.access_key_id, self.access_key_secret, http_method, custom_params)
        resp = jy_requests.request(http_method, self.address, params=params)
        return resp

    def attach_policy_to_user(self, user_name, policy_name, policy_type=None):
        """

        :param user_name:
        :param policy_name:
        :param policy_type: Custom System
        :return:
        """
        action = "AttachPolicyToUser"
        http_method = "GET"
        if policy_type is None:
            if policy_name.find("_") >= 0:
                policy_type = "Custom"
            else:
                policy_type = "System"
        custom_params = dict(Action=action, UserName=user_name, PolicyName=policy_name, PolicyType=policy_type)
        params = get_params(self.access_key_id, self.access_key_secret, http_method, custom_params)
        resp = jy_requests.request(http_method, self.address, params=params)
        return resp

    def detach_policy_to_user(self, user_name, policy_name):
        action = "DetachPolicyFromUser"
        http_method = "GET"
        custom_params = dict(Action=action, UserName=user_name, PolicyName=policy_name, PolicyType="Custom")
        params = get_params(self.access_key_id, self.access_key_secret, http_method, custom_params)
        resp = jy_requests.request(http_method, self.address, params=params)
        return resp

    def list_policies_for_user(self, user_name):
        action = "ListPoliciesForUser"
        http_method = "GET"
        custom_params = dict(Action=action, UserName=user_name)
        params = get_params(self.access_key_id, self.access_key_secret, http_method, custom_params)
        resp = jy_requests.request(http_method, self.address, params=params)
        return resp

    def detach_all_policy_to_user(self, user_name):
        lr = self.list_policies_for_user(user_name).data
        if lr is None:
            return
        policies = lr["Policies"]["Policy"]
        for item in policies:
            self.detach_policy_to_user(user_name, item["PolicyName"])

    def delete_user_force(self, user_name):
        self.detach_all_policy_to_user(user_name)
        self.delete_user(user_name)


if __name__ == "__main__":
    import os
    from JYAliYun.AliYunAccount import RAMAccount
    account = RAMAccount(conf_path="/data/Web2/conf/oss.conf")
    ram_man = RAMUserManager(ram_account=account)
    # list_r = ram_man.list_users()
    # p_dir = "/mnt/data/ali_policy"
    # policy_docs = os.listdir(p_dir)
    # all_policies = []
    # for doc in policy_docs:
    #     doc_path = os.path.join(p_dir, doc)
    #     with open(doc_path) as rd:
    #         p_name = doc[:-7]
    #         ram_man.delete_policy(p_name)
    #         r = ram_man.create_policy(p_name, rd.read())
    #         all_policies.append(p_name)
    user_name = "vipingjo"
    reps = ram_man.get_user(user_name)
    print(reps.text)
    print(ram_man.list_access_keys(user_name).data)
    # ram_man.delete_user_force(user_name)
    # cur = ram_man.create_user("be_developer", display_name="Back End Developer", mobile_phone="15290539544",
    #                           comments="后端开发人员专属的子帐号", email="zhouheng@genen.ac")
    # print(cur.text)
    # ram_man.detach_all_policy_to_user(user_name)
    # for item in all_policies:
    #     ram_man.attach_policy_to_user(user_name, item)
    # ram_man.create_access_key(user_name).text