# Copyright (C) 2016-2017,BGI ltd.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may not
#   use this file except in compliance with the License. You may obtain a copy
#   of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import bgionline

urls = {
    "login": "/access/login",
    "refreshToken": "/access/refreshToken",
    "project": {
        "create": "/project",
        "job": "/project/%s/job",
        "file": "/project/%s/file",
        "forceOwnership": "/project/%s/forceOwnership",
        "addMember": "/project/%s/addMember"
    },
    "user": {
        "create": "/user",
        "changeStatus": "/user/%s/status",
        "claimToken": "/user/%s/claimToken",
        "project": "/user/%s/project"
    },
    "job": {
        "create": "/job",
        "view": "/job/%s",
        "file": "/job/%s/file"
    },
    "app": {
        "public": "/app/public",
        "clone": "/app/%s/clone",
        "info": "/app/%s"
    },
    "file": {
        "download": "/file/%s/download",
        "delete": "/file/%s",
        "meta": "/file/%s/meta"
    },
    "message": {
        "send": "/message",
        "get": "/message",
    },
    "time": "/time"
}


def user_create(input_params={}, always_retry=True, **kwargs):
    return bgionline.APIRequest("/user", input_params, always_retry=always_retry, **kwargs)


def user_projects(username, input_params={}, always_retry=True, **kwargs):
    return bgionline.APIRequest("/user/%s/project" % username, method="GET", data=input_params,
                                always_retry=always_retry, **kwargs)


def project_create(input_params={}, always_retry=True, **kwargs):
    return bgionline.APIRequest("/project", input_params, always_retry=always_retry, **kwargs)


def get_ids_by_path(input_params={}, always_retry=True, **kwargs):
    return bgionline.APIRequest("/file/getIdsByPath", method="GET", params=input_params,
                                always_retry=always_retry, **kwargs)


def delete_files(file_id, input_params={}, always_retry=True, **kwargs):
    return bgionline.APIRequest("/file/%s" % file_id, method="DELETE", params=input_params,
                                always_retry=always_retry, **kwargs)


def get_folder_list(input_params={}, always_retry=True, **kwargs):
    return bgionline.APIRequest("/folder/list", method="GET", params=input_params,
                                always_retry=always_retry, **kwargs)


def new_folder(project_id, input_params={}, always_retry=False, **kwargs):
    return bgionline.APIRequest("/project/%s/file/newFolder" % project_id, method="POST", data=input_params,
                                always_retry=always_retry, **kwargs)


def new_file(project_id, input_params={}, always_retry=True, **kwargs):
    return bgionline.APIRequest("/project/%s/file/new" % project_id, method="POST", data=input_params,
                                always_retry=always_retry, **kwargs)


def get_sts_token(input_params={}, always_retry=True, **kwargs):
    return bgionline.APIRequest("/project/%s/file/refreshUploadToken" % bgionline.config.current_project_id,
                                method="GET", params=input_params,
                                always_retry=always_retry, **kwargs)


def updata_file_status(project_id, input_params={}, always_retry=True, **kwargs):
    return bgionline.APIRequest("/project/%s/file/callback" % project_id, method="POST", json=input_params,
                                always_retry=always_retry, **kwargs)


def get_token_info(input_params={}, always_retry=True, **kwargs):
    return bgionline.APIRequest("/access/getTokenInfo", method="GET", params=input_params,
                                always_retry=False, **kwargs)


def get_download_info(file_id, input_params={}, always_retry=True, **kwargs):
    return bgionline.APIRequest("/file/%s/bucketInfo" % file_id, method="GET", params=input_params,
                                always_retry=always_retry, **kwargs)


def change_parent(input_params={}, always_retry=True, **kwargs):
    return bgionline.APIRequest("/file/changeparent", method="POST", data=input_params,
                                always_retry=always_retry, **kwargs)


def file_rename(file_id, input_params={}, always_retry=True, **kwargs):
    return bgionline.APIRequest("/file/%s" % file_id, method="PUT", data=input_params,
                                always_retry=always_retry, **kwargs)


def transfer(project_id, input_params={}, always_retry=True, **kwargs):
    return bgionline.APIRequest("/project/%s/ownership" % project_id, method="POST", data=input_params,
                                always_retry=always_retry, **kwargs)


def transfer_user(user_name, always_retry=True, **kwargs):
    return bgionline.APIRequest("/user/%s/claimToken" % user_name, method="POST",
                                always_retry=always_retry, **kwargs)


def get_project_folders(porject_id, input_params={}, always_retry=True, **kwargs):
    return bgionline.APIRequest("/project/%s/getFoldersByPorjectId" % porject_id, method="GET", params=input_params,
                                always_retry=always_retry, **kwargs)


def get_project_job(porject_id, input_params={}, always_retry=True, **kwargs):
    return bgionline.APIRequest("/project/%s/job" % porject_id, method="GET", params=input_params,
                                always_retry=always_retry, **kwargs)


def get_project_app(porject_id, input_params={}, always_retry=True, **kwargs):
    return bgionline.APIRequest("/project/%s/app" % porject_id, method="GET", params=input_params,
                                always_retry=always_retry, **kwargs)


def file_list(porject_id, url, input_params={}, always_retry=True, **kwargs):
    return bgionline.APIRequest("/project/%s/file%s" % (porject_id, url), method="GET", params=input_params,
                                always_retry=always_retry, **kwargs)


def get_download_link(file_id, input_params={}, always_retry=True, **kwargs):
    return bgionline.APIRequest("/file/%s/download" % file_id, method="GET", params=input_params,
                                always_retry=always_retry, **kwargs)


def get_file_info(file_id, input_params={}, always_retry=True, **kwargs):
    return bgionline.APIRequest("/file/%s" % file_id, method="GET", params=input_params,
                                always_retry=always_retry, **kwargs)