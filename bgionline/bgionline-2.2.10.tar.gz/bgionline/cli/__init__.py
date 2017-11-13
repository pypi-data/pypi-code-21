# -*- coding: utf-8 -*-
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
from __future__ import print_function
import sys

reload(sys)
sys.setdefaultencoding('utf8')

import sys
import os
import bgionline
import getpass
import traceback
import multiprocessing
import json
import pprint
import time
import shlex
import string
import csv
import fnmatch
import argparse

from bgionline.utils.sh_util import BOCompleter
from bgionline import scripts
from bgionline import logger, config
from bgionline.exceptions import APIError, err_exit
from bgionline.utils import prettytable, parse_size, try_call, forge_random_string, get_fully_path, choices_project, \
    to_zhcn, get_files_info, progress, multiprocessing_daemon, set_config, del_punctuation, parse_time, format_tree, \
    format_time, split_project_path
from bgionline.utils.upload_file import OSTYPE, upload_file, upload_directory, upload_file_consumer, \
    show_upload_progress
from bgionline.utils.print_funtion import (RED, GREEN, BLUE, YELLOW, WHITE, BOLD, UNDERLINE, ENDC)
from bgionline.utils.download_file import download_dir, download_file, download_file_consumer, show_progress

PATH_MATCHES = []


def login(args):
    host = args.host
    port = args.port
    token = args.token
    protocol = args.protocol
    storage_host = args.storage
    bgionline.set_server_info(host=host, port=port, protocol=protocol, storage_host=storage_host)
    bgionline.update_server_info(args.config)

    print("Logging into %s" % bgionline.API_SERVER)

    attempt = 0
    if token:
        try:
            data = {
                'token': token
            }

            res = bgionline.api.get_token_info(input_params=data)

        except (KeyboardInterrupt, EOFError):
            sys.exit(0)
        except Exception as e:
            err_exit(e)
        bgionline.set_username(res["username"], args.config)
        bgionline.set_auth_token(res["accessToken"], args.config)
    else:
        while attempt < 3:
            if config.username:
                username = raw_input("Username [%s]: " % config.username)
            else:
                username = raw_input("Username: ")

            if not username:
                if config.username:
                    username = config.username
                else:
                    continue
            bgionline.set_username(username, args.config)
            password = getpass.getpass()

            data = {"username": username, "password": password}
            try:
                res = bgionline.APIRequest("/access/login", data)
                break
            except (KeyboardInterrupt, EOFError):
                sys.exit(0)
            except APIError as e:
                if e.name == "Unauthorized":
                    print("Incorrect username and/or password")
                    attempt += 1
                    continue
                else:
                    err_exit(e)
            except Exception as e:
                err_exit(e)

        # end of while
        bgionline.set_auth_token(res["accessToken"], args.config)
    print("You are now logged in. Your configurations are stored in %s. " % config.get_user_config())

    if args.projects:
        print("\nUse bo select to choose your working project...")
        args.project = None
        try_call(select, args)


@set_config
def logout(args):
    if config.security_token:
        print("Logging out from %s and remove credentials." % bgionline.API_SERVER)
        try:
            res = bgionline.APIRequest("/access/logout", {})

        except (KeyboardInterrupt, EOFError):
            sys.exit(0)

        except APIError as e:
            err_exit(e)

        except Exception as e:
            print(traceback.print_exc(e))
            err_exit(e)

        if os.path.exists(config.user_config_dir + os.sep + 'setting'):
            os.remove(config.user_config_dir + os.sep + 'setting')


def _list_user_projects(username):
    projects = []
    try:
        projects = bgionline.api.user_projects(username)

    except (KeyboardInterrupt, EOFError):
        sys.exit(0)
    except APIError as e:
        err_exit(e)

    except Exception as e:
        print(traceback.print_exc(e))
        err_exit(e)

    return projects


def get_tree(input, output=[], prefix=u'│', show_id=False, show_only_folder=False):
    if input.get('children') is not None:
        if input.get('name') is not None:
            # 加颜色显示
            info = BOLD(BLUE(input.get('name')))
            if prefix[-4:] == '    ':
                output.append('%s%s%s' % (to_zhcn(prefix.encode('utf-8')[:-4]), to_zhcn(u'  └──'), info))
            elif prefix[-4:] == "":  # 判断是否是最后一个
                output.append('%s%s%s' % (to_zhcn(prefix.encode('utf-8')[:-4]), to_zhcn(u'└──'), info))
            else:
                output.append(
                    '%s%s%s' % (to_zhcn(to_zhcn(prefix.encode('utf-8')[:-4])), to_zhcn(to_zhcn(u'├──')), info))

        if input['children'].__len__() is not 0:
            for index, i in enumerate(input['children']):
                if input.get('name'):  # 判断是否是第一次函数
                    if index + 1 == len(input['children']):  # 判断是否是最后一次递归
                        get_tree(i, output, prefix + u'     ', show_id, show_only_folder)
                    else:
                        get_tree(i, output, prefix + u'   │ ', show_id, show_only_folder)
                else:
                    if index + 1 == len(input['children']):  # 判断是否是最后一次递归
                        get_tree(i, output, "", show_id, show_only_folder)
                    else:
                        get_tree(i, output, prefix, show_id, show_only_folder)
    if not show_only_folder:
        if input.get('name') and int(input.get('isFolder')) == 0:
            if show_id:  # 判断是否需要显示id
                info = '%s [%s]' % (input.get('name'), input.get('id'))
            else:
                info = input.get('name')
            if prefix[-4:] == '    ':  # 判断是否是最后一个
                output.append('%s%s%s' % (to_zhcn(prefix.encode('utf-8')[:-4]), u'  └── ', info))
            elif prefix[-4:] == "":
                output.append('%s%s%s' % (to_zhcn(prefix.encode('utf-8')[:-4]), u'└── ', info))
            else:
                output.append('%s%s%s' % (to_zhcn(prefix.encode('utf-8')[:-4]), u'├── ', info))
    else:
        if prefix[-4:] == '    ' or prefix[-4:] == "":  # 如果最后一个不是文件夹，那么就把文件夹的├──替换
            output[-1] = output[-1].replace(to_zhcn(u'├──'), to_zhcn(u'└──'))


def _list_files(path, multi_level=False, project_id=None, carry=True):
    if multi_level:
        multi_level = 'true'
    else:
        multi_level = 'false'

    if carry:
        carry = 'true'
    else:
        carry = 'false'

    files = []
    try:
        data = {
            'projectId': project_id or config.current_project_id,
            'path': (to_zhcn(path)).encode('utf-8'),
            'multiLevel': multi_level,
            'carry': carry
        }
        files = bgionline.api.get_folder_list(input_params=data, always_retry=False)

    except (KeyboardInterrupt, EOFError):
        sys.exit(0)
    except APIError as e:
        err_exit(e)

    except Exception as e:
        print(traceback.print_exc(e))
        err_exit(e)

    return files


def _list_project_files(project_id):
    pass


@set_config
def select(args):
    try:
        projects = _list_user_projects(config.username)
    except Exception as e:
        print("Error when listing projects")
        err_exit(e)

    id_or_name = args.project

    if args.project is not None:
        projects = find_projects(args.project, projects)
        if len(projects) == 0:
            err_exit("Could not find a project named '%s'" % id_or_name)
        elif len(projects) == 1:
            config.current_project_id = projects[0]["id"]
            config.current_project_name = projects[0]["name"]
            config.current_path_id = None
            config.current_wd = '/'
            config.save()
            print("Setting current project to: %s \n" % projects[0]["name"])
            return

    if len(projects) == 0:
        print("There is no projects to choose from.")

    print("\nAvailable projects:\n" if not id_or_name else "")

    pick = choices_project(projects, default_choices_id=config.current_project_id,
                           show_info=['id', 'name'], show_info_name=['project id', 'project name'])

    config.current_project_id = projects[pick]["id"]
    config.current_project_name = projects[pick]["name"]
    config.current_path_id = None
    config.current_wd = '/'
    config.save()
    print("Setting current project to: %s " % to_zhcn(projects[pick]["name"]))


def find_projects(id_or_name=None, project=None):
    projects = project or _list_user_projects(username=config.username)
    results = []
    for p in projects:
        if id_or_name == p["id"] or id_or_name == p["name"]:
            results.append(p)
    return results


def find_files(path, id_or_name=None, project_id=None, multiLevel=False, fuzzy_match=False, files=None, dirs=True,
               file_type=None, carry=True):
    files = files or _list_files(path, multi_level=multiLevel, project_id=project_id, carry=carry)
    output = []
    output = _filter_files(output, files, id_or_name, fuzzy_match=fuzzy_match, dirs=dirs, file_type=file_type)
    return output


def _filter_files(output, input, filter_id_or_name=None, fuzzy_match=False, dirs=True, file_type=None):
    if input.get('children'):
        if input['children'].__len__() is not 0:
            for i in input['children']:
                _filter_files(output, i, filter_id_or_name, fuzzy_match, dirs=dirs, file_type=file_type)
    if not dirs and (input.get('isFolder') == '1' or input.get('isFolder') == 1):
        return output
    if file_type is None or (input.get('name') and fnmatch.fnmatch(input.get('name'), file_type)):
        if input.get('name') and (filter_id_or_name is None or input.get('name') == filter_id_or_name or
                                          input.get('id') is filter_id_or_name or (
                    fuzzy_match and filter_id_or_name in input.get('name'))):
            output.append(input)
    return output


def check_username_format(username):
    if len(username) < 4:
        return False
    limitation = list(string.ascii_lowercase + string.digits + "_" + string.ascii_uppercase)
    for i in username:
        if i not in limitation:
            return False
    else:
        return True


@set_config
def new_user(args):
    name = args.name

    if not check_username_format(name):
        print("User name must be between 4 and 40 characters and contain alphanumeric characters and underscores only")
        return

    if args.password:
        if len(args.password) > 30 or len(args.password) < 8:
            err_exit('User password must be between 8 and 30 characters')
    # random generate password and email if not provided
    password = forge_random_string() if args.password is None else args.password
    email = forge_random_string() + "@random-generated.addr" if args.email is None else args.email

    # todo more roles
    role = 1
    data = {'username': name, 'password': password, 'email': email, 'role': role}

    try:
        res = bgionline.api.user_create(data)
    except (KeyboardInterrupt, EOFError) as e:
        logger.debug("interrupted by user")
        err_exit("Keyboard Interrupted.")
    except Exception as e:
        err_exit(e)

    if not args.password:
        try:
            res = bgionline.api.transfer_user(name)
            token = res['token']
            claim_token = "%s://%s#/account/transfer?username=%s&token=%s" % (config.protocol, config.host, name, token)
            print("%s has been created" % name)
            print('claim_token:  %s' % claim_token)
            print('Validity period: 30 Day')
            return
        except Exception as e:
            err_exit(e)

    print("%s has been created" % res["id"])


@set_config
def new_project(args):
    name = args.name
    desc = args.desc

    data = {"name": (to_zhcn(name)).encode('utf-8'), "description": desc}

    try:
        res = bgionline.api.project_create(data)
    except (KeyboardInterrupt, EOFError) as e:
        logger.debug("interrupted by user")
        err_exit("Keyboard Interrupted.")
    except Exception as e:
        err_exit(e)

    # todo
    project_id = args.project = res["id"]

    if not args.select:
        print(project_id)
        return
    try:
        select(args)
    except Exception as e:
        print(traceback.print_exc(e))


@set_config
def pwd(args):
    if config.current_project_name in ("None", None):
        err_exit("Current project is not set")

    print(to_zhcn("%s:%s" % (config.current_project_name, config.current_wd)))


@set_config
def cd(args):
    if args.path == '..':
        if config.current_wd != '/':
            path = os.path.dirname(os.path.dirname(get_fully_path(args.path)[:-1]))
            if path != '/':
                path = path + '/'
            data = {'path': path, 'projectId': config.current_project_id}
        else:
            return
    else:
        data = {'path': (to_zhcn(get_fully_path(args.path))).encode('utf-8'), 'projectId': config.current_project_id}

    if data.get('path') == '/':
        config.current_wd = '/'
        config.current_path_id = None
        config.save()
        return

    try:
        res = bgionline.api.get_ids_by_path(input_params=data, always_retry=False)
        config.current_wd = (to_zhcn(data.get('path'))).encode('utf-8')
        config.current_path_id = res['ids'][0]
        config.save()
    except Exception as e:
        err_exit(e)


@set_config
def mv(args):
    # 1获取文件id
    destination_id = ""
    sources_id = ""
    try:
        data = {'path': get_fully_path(args.sources, is_end=args.sources[-1] is '/'),
                'projectId': config.current_project_id}
        res = bgionline.api.get_ids_by_path(input_params=data, always_retry=False)
        sources_id = res['ids'][0]
        sources_parent = res['parent']
    except Exception as e:
        err_exit(e)
    # 2 获取目标位置的id
    if os.path.dirname(args.destination):
        try:
            data = {'path': get_fully_path(os.path.dirname(args.destination)), 'projectId': config.current_project_id}
            if data['path'] is '/' or data['path'] is None:
                destination_id = ""
            else:
                res = bgionline.api.get_ids_by_path(input_params=data, always_retry=False)
                destination_id = res['ids'][0]
        except Exception as e:
            err_exit(e)
    # 3、移动文件夹
    if sources_parent != destination_id and (sources_parent is None and destination_id != ''):
        try:

            data = {'fileId': sources_id, 'parentId': destination_id}
            bgionline.api.change_parent(input_params=data)
        except Exception as e:
            err_exit(e)
    # 4、重命名文件
    if args.destination[-1] is not '/':
        try:
            data = {'name': os.path.basename(args.destination)}
            bgionline.api.file_rename(sources_id, input_params=data)
        except Exception as e:
            err_exit(e)


@set_config
def rm(args):
    if args.id is None and args.path is None:
        print('You must enter file_path or file_id')
        return
    if args.id is not None:
        try:
            bgionline.api.delete_files(args.id)
        except Exception as e:
            if e.message == 'Page not found.':
                print('No such file or directory found in project %s[%s]' % (
                    config.current_project_name, config.current_project_id))
            else:
                err_exit(e)
    else:
        if args.path[-1] is '/':
            data = {'path': get_fully_path(args.path), 'projectId': config.current_project_id}
            try:
                res = bgionline.api.get_ids_by_path(input_params=data, always_retry=False)
                bgionline.api.delete_files(res['ids'][0])
            except Exception as e:
                err_exit(e)
        else:
            try:
                print (get_fully_path(os.path.dirname(args.path), False))
                print (os.path.basename(args.path))
                files = find_files(get_fully_path(os.path.dirname(args.path), False), os.path.basename(args.path))
            except Exception as e:
                print(e)

            if len(files) == 0:
                err_exit("No such file or directory")
            elif len(files) == 1:
                file_id = files[0]["id"]
            else:
                index = choices_project(files, show_info=['id', 'name', 'size'])
                file_id = files[index]["id"]
            try:
                bgionline.api.delete_files(file_id)
            except Exception as e:
                if e.message == 'Page not found.':
                    print('No such file or directory found in project %s[%s]' % (
                        config.current_project_name, config.current_project_id))
                else:
                    err_exit(e)


@set_config
def mkdir(args):
    project_id, path = split_project_path(args.paths)
    data = {'path': path, 'projectId': project_id or bgionline.config.current_project_id}

    # 先判断文件夹是否存在，如果不存在才创建
    try:
        bgionline.api.get_ids_by_path(input_params=data, always_retry=False)
        print('Error: Cannot create folder: already exists')
        return
    except Exception as e:
        if e.message != 'backend_msg_no_this_folder':
            err_exit(e)

    if path[-1] is '/':
        path = path[0:-1]
    if path != '/' and path[0] == '/':
        path = path[1:]
    data = {
        'currentPath': '/',
        'path': (to_zhcn(path)).encode('utf-8'),
        'parents': args.parents
    }

    try:
        bgionline.api.new_folder(project_id or bgionline.config.current_project_id, input_params=data)
    except Exception as e:
        err_exit(e)


@set_config
def ls(args):
    project_id = None
    if args.path is None:
        path = get_fully_path("", is_end=False)
    else:
        project_id, path = split_project_path(args.path)

    if path != '/' and path[-1] is '/':
        path = path[0:-1]

    file_list = find_files(path, project_id=project_id)

    # 显示文件夹
    for i in file_list:
        if i.get('isFolder'):
            message = i.get('name') + '/'
            if args.id:
                message = message + '[' + i.get('id') + ']'
            print(to_zhcn(BOLD(BLUE(message.encode('utf-8')))))

    # 显示文件
    if not args.folders:
        for i in file_list:
            if not i.get('isFolder'):
                message = i.get('name')
                if args.id:
                    message = message + '[' + i.get('id') + ']'
                print(to_zhcn(message.encode('utf-8')))


@set_config
def tree(args):
    project_id = None
    if args.path is None:
        path = get_fully_path("", is_end=False)
    else:
        project_id, path = split_project_path(args.path)

    if path != '/' and path[-1] is '/':
        path = path[0:-1]

    if OSTYPE == 'windows':
        path = to_zhcn(path)

    def format_tree_data(in_data, parent_id=''):
        '''
        格式化树形的数据
        :param in_data: 需要格式化的数据
        :param parent_id: 根id
        :return:
        '''
        if parent_id is None or parent_id == 'None':
            parent_id = ''
        tree = {}
        id_lest = []

        def find_node(tree, i, j, id_lest):
            if tree['id'] == j:
                tree['node'].update({i['name']: {'id': i['id'], 'node': {}}})
                id_lest.append(i['id'])
            else:
                if tree['node']:
                    for x in tree['node']:
                        find_node(tree['node'][x], i, j, id_lest)

        def del_node(tree):
            for i in tree:
                tree[i] = tree[i].pop('node')
                del_node(tree[i])

        for i in in_data:
            if i['parent'] == parent_id:
                tree.update({i['name']: {'id': i['id'], 'node': {}}})
                id_lest.append(i['id'])
        for x in id_lest:
            for y in in_data:
                if y['parent'] == x:
                    for z in tree:
                        find_node(tree[z], y, x, id_lest)

        del_node(tree)
        return tree

    file_list = _list_files(path, True, project_id=project_id, carry=args.file)
    gettree = [BOLD(BLUE(path))]

    get_tree(input=file_list, output=gettree, show_id=args.id)
    print(to_zhcn('\n'.join(gettree)))

    # if args.file:
    #     file_list = _list_files(path, True, project_id=project_id)
    #     gettree = [BOLD(BLUE(path))]
    #
    #     get_tree(input=file_list, output=gettree, show_id=args.id)
    #     print(to_zhcn('\n'.join(gettree)))
    # else:
    #     path_id = None
    #     if path and path != '/':
    #         data = {'path': get_fully_path(path), 'projectId': project_id or config.current_project_id}
    #         try:
    #             res = bgionline.api.get_ids_by_path(input_params=data)
    #             path_id = res['ids'][0]
    #         except Exception as e:
    #             err_exit(e)
    #     try:
    #         res = bgionline.api.get_project_folders(project_id or config.current_project_id)
    #     except Exception as e:
    #         err_exit(e)
    #     tree = format_tree_data(res, path_id or config.current_path_id)
    #     print(BLUE(BOLD(to_zhcn(format_tree(tree, path)))))


@set_config
def upload(args):
    project_id = None
    path = None
    parent_id = None
    if args.bgionline_path is not None:
        if ':' in args.bgionline_path:
            project_id, path = args.bgionline_path.split(':')
    if project_id is None:
        if config.current_project_id is None:
            print("\nUse bo select to choose your working project...")
            args.project = None
            try_call(select, args)
        project_id = config.current_project_id
        path = get_fully_path(args.bgionline_path)

    if args.concurrent > 5 or args.concurrent < 1:
        err_exit('The number of concurrent tasks, the default is 1, the maximum is 5')

    if not os.path.exists(args.local_path):
        err_exit("%s: No such file or directory" % args.local_path)
    metadatafile_dist = {}

    metadata = ""
    for i in args.metadata:
        if len(i.split('=')) != 2 or i.endswith('=') or i.startswith('='):
            err_exit('Metadata invalid syntax, Syntax: -m key=value')
        metadata = i + "|" + metadata

    if args.metadatafile is not None:
        if not os.path.exists(args.metadatafile):
            err_exit("%s No such file or directory" % args.metadatafile)
        if os.path.splitext(args.metadatafile)[-1] != '.csv':
            print(os.path.splitext(args.metadatafile)[-1])
            err_exit("Metadata file must be a CSV file")
        metadata_file_path = os.path.realpath(args.metadatafile)
        with open(metadata_file_path, 'rb') as csvfile:
            reader = csv.DictReader(csvfile)
            keys = list(reader.fieldnames)
            if 'filePath' not in keys:
                err_exit("CSV File invalid syntax, you must include the 'filePath' column")
            keys.remove('filePath')
            for row in reader:
                row_dist = {}
                for i in keys:
                    row_dist.update({i: row[i]})
                metadatafile_dist.update({row['filePath']: row_dist})

    if path != '/':
        try:
            data = {'path': path, 'projectId': project_id}
            res = bgionline.api.get_ids_by_path(input_params=data, always_retry=False)
            parent_id = res['ids'][0]
        except Exception as e:
            if e.message == 'backend_msg_no_this_folder':
                print('%s:  The folder could not be found in %s[%s]' % (
                    path, config.current_project_name, config.current_project_id))
                exit()
            else:
                err_exit(e)

    file_path = os.path.realpath(args.local_path)

    # # 清除一天前的恢复文件
    # for i in os.listdir(config.user_config_dir):
    #     if '.upload.record' in i:
    #         if time.time() - os.stat(config.user_config_dir + os.sep + i)[8] > 86400:
    #             os.remove(config.default_config_dir + os.sep + i)
    start_time = time.time()
    lock = multiprocessing.Lock()
    upload_record_f = bgionline.config.user_config_dir + os.sep + del_punctuation(
        project_id + path + os.path.abspath(file_path)) + '.upload.record'
    upload_record_dict = {}
    file_count, total, file_name_list = get_files_info(file_path)

    if os.path.isfile(upload_record_f):
        is_continue = True
        if not args.force:
            choice = raw_input(
                "This operation already exists, would you like to continue? "
                "[Yes]/No: ")  # % BOLD(RED(str(sum_file))))
            if choice is not None and choice.lower().startswith('n'):
                is_continue = False
        if is_continue:
            if OSTYPE == 'windows':
                import io
                with io.open(upload_record_f, 'r', encoding='windows-1252') as f:
                    upload_record_dict = json.load(f)
            else:
                with open(upload_record_f, 'r') as f:
                    upload_record_dict = json.load(f)
    if os.path.isdir(file_path):
        if args.concurrent == 1:
            queue = None
        else:
            queue = multiprocessing.JoinableQueue()
            upload_record = {}
            # upload_record = multiprocessing.Manager().dict()
        try:
            path = get_fully_path(path, False)
            upload_directory(upload_record_dict, upload_record_f, lock, metadata, metadatafile_dist, queue, project_id,
                             file_path,
                             metadata, path, args.wildcard)
            upload_record = multiprocessing.Manager().dict(upload_record_dict)
        except Exception as e:
            print(e)
        if args.concurrent != 1:
            list_pid = []
            print_location = dict()

            # 开启多进程下载
            if OSTYPE != "windows":
                err_file = []
                succeed_file = []
                consumed = 0
                from bgionline.utils import TERM
                with TERM.fullscreen():
                    for i in range(args.concurrent):
                        cons = multiprocessing.Process(target=upload_file_consumer,
                                                       args=(
                                                           queue, upload_record, upload_record_f, lock, consumed,
                                                           err_file, succeed_file, (0, i)))
                        cons.daemon = True
                        cons.start()
                        list_pid.append(cons.pid)
                        print_location[cons.pid] = i
            else:
                err_file = multiprocessing.Manager().list()
                succeed_file = multiprocessing.Manager().list()
                consumed = multiprocessing.Manager().Value('i', 0)
                for i in range(args.concurrent):
                    cons = multiprocessing.Process(target=upload_file_consumer,
                                                   args=(
                                                       queue, upload_record, upload_record_f, lock, consumed, err_file,
                                                       succeed_file, (0, i)))
                    cons.daemon = True
                    cons.start()
                    list_pid.append(cons.pid)
                    print_location[cons.pid] = i
                # 显示进度条
                show_progres = multiprocessing.Process(target=show_upload_progress, args=(
                    consumed, total, file_count, err_file, succeed_file, list_pid, queue))
                show_progres.start()
                list_pid.append(show_progres.pid)
            multiprocessing_daemon(multiprocessing, queue, list_pid, upload_file_consumer, upload_record,
                                   upload_record_f,
                                   lock, consumed, err_file, succeed_file, print_location)
            queue.join()

            # 等待进度条信息同步
            time.sleep(2)
            for i in list_pid:
                os.kill(i, 9)
    else:
        file_name_list = [file_path]
        upload_file(upload_record_dict, upload_record_f, lock, project_id,
                    parent_id, file_path, metadata, metadatafile_dist, show_progres=progress)

    # 确定完整性
    if OSTYPE == 'windows':
        upload_record_f = to_zhcn(upload_record_f)
        import io
        if os.path.isfile(upload_record_f):
            with io.open(upload_record_f, 'r', encoding='windows-1252') as f:
                upload_record_dict = json.load(f)
    else:
        if os.path.isfile(upload_record_f):
            with open(upload_record_f, 'r') as f:
                upload_record_dict = json.load(f)
    for i in upload_record_dict:
        if upload_record_dict[i]['status'] == 2:
            if OSTYPE == 'windows':
                i = (to_zhcn(i)).encode('windows-1252')
            file_name_list.remove(i)
    if len(file_name_list) == 0:
        if os.path.isfile(upload_record_f):
            os.remove(upload_record_f)
    else:
        for i in file_name_list:
            print('Error file %s' % i)

    print()
    print('This task took %s\t\t%s/s' % (
        parse_time(time.time() - start_time), parse_size(total / (time.time() - start_time))))


@set_config
def download(args):
    start_time = time.time()
    project_id = None
    path = None
    is_download_file = False
    if args.bgionline_path is not None:
        if ':' in args.bgionline_path:
            project_id, args.bgionline_path = args.bgionline_path.split(':')
    if args.bgionline_path is not None and args.bgionline_path[-1] is not '/':
        is_download_file = True
    else:
        if args.bgionline_path:
            if args.bgionline_path[-1] is '/':
                args.bgionline_path = args.bgionline_path[0:-1] or args.bgionline_path
    if project_id is None:
        if config.current_project_id is None:
            print("\nUse bo select to choose your working project...")
            args.project = None
            try_call(select, args)
        project_id = config.current_project_id
    if not args.bgionline_path:
        args.bgionline_path = config.current_wd
    path = get_fully_path(args.bgionline_path, is_end=False)

    if args.concurrent > 5 or args.concurrent < 1:
        print('The number of concurrent tasks, the default is 1, the maximum is 5')
        sys.exit(1)

    # path = args.path or config.current_wd
    output_dir = args.local_path
    if OSTYPE == 'windows':
        output_dir = to_zhcn(output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    lock = multiprocessing.Lock()
    download_record_f = bgionline.config.user_config_dir + os.sep + del_punctuation(
        project_id + path + os.path.abspath(output_dir)) + '.download.record'
    download_record_dict = {}

    if os.path.isfile(download_record_f):
        is_continue = True
        if not args.force:
            choice = raw_input(
                "This operation already exists, would you like to continue? "
                "[Yes]/No: ")  # % BOLD(RED(str(sum_file))))
            if choice is not None and choice.lower().startswith('n'):
                is_continue = False
        if is_continue:
            if OSTYPE == 'windows':
                download_record_f = to_zhcn(download_record_f)
                import io
                with io.open(download_record_f, 'r', encoding='windows-1252') as f:
                    download_record_dict = json.load(f)
            else:
                with open(download_record_f, 'r') as f:
                    download_record_dict = json.load(f)

    download_name_list = []
    if is_download_file:
        try:

            try:
                files = find_files(os.path.dirname(path), os.path.basename(path), project_id=project_id)
            except Exception as e:
                print(e)

            if len(files) == 0:
                err_exit("No such file or directory")
            elif len(files) == 1:
                file_id = files[0]["id"]
                index = 0
            else:
                index = choices_project(files, show_info=['id', 'size', 'createdAt'])
                file_id = files[index]["id"]

            download_size = 0
            if files[index]['status'] != 2:
                print('Download failed, this file does not support download')
                return
            file_info = {
                'id': file_id,
                'name': os.path.basename(path),
                'local_path': output_dir
            }
            download_name_list.append(os.path.join(output_dir, file_info['name']))
            download_size += (files[index]['size'])
            download_file(download_record_dict, download_record_f, lock, file_info, show_progres=progress)
            print()
        except Exception as e:
            err_exit(e)
    else:
        if path != '/':
            output_dir = os.path.join(output_dir, os.path.basename(path))
        if args.concurrent == 1:
            queue = None
        else:
            queue = multiprocessing.JoinableQueue()
            download_record_dict = multiprocessing.Manager().dict(download_record_dict)
        download_size_list = []
        try:
            data = {'path': path, 'projectId': project_id}
            if data['path'] == '/':
                path_id = ''
            else:
                data['path'] = path + '/'

                if data['path'] == config.current_wd:
                    path_id = config.current_path_id
                else:
                    path_id = (bgionline.api.get_ids_by_path(input_params=data, always_retry=False))['ids'][0]

            if not args.force:
                choice = raw_input(
                    "Download files this action altogether, there will be a fee, do you need this operation? "
                    "[Yes]/No: ")  # % BOLD(RED(str(sum_file))))
                if choice is not None and choice.lower().startswith('n'):
                    return 0
            download_dir(download_record_dict, download_record_f, lock, queue, project_id, path_id, args.wildcard,
                         download_size_list, download_name_list,
                         local_path=output_dir)
        except Exception as e:
            err_exit(e)
        download_size = 0
        for i in download_size_list:
            download_size = download_size + i
        if args.concurrent != 1:
            list_pid = []
            print_location = dict()

            if OSTYPE != "windows":
                err_file = []
                succeed_file = []
                consumed = 0
                from bgionline.utils import TERM
                with TERM.fullscreen():
                    for i in range(args.concurrent):
                        cons = multiprocessing.Process(target=download_file_consumer,
                                                       args=(
                                                           queue, download_record_dict, download_record_f, lock,
                                                           consumed, err_file, succeed_file, (0, i)))
                        cons.daemon = True
                        cons.start()
                        list_pid.append(cons.pid)
                        print_location[cons.pid] = i
            else:
                err_file = multiprocessing.Manager().list()
                succeed_file = multiprocessing.Manager().list()
                consumed = multiprocessing.Manager().Value('i', 0)
                for i in range(args.concurrent):
                    cons = multiprocessing.Process(target=download_file_consumer,
                                                   args=(queue, download_record_dict, download_record_f, lock, consumed,
                                                         err_file, succeed_file, (0, i)))
                    cons.daemon = True
                    cons.start()
                    list_pid.append(cons.pid)
                    print_location[cons.pid] = i
                show_progres = multiprocessing.Process(target=show_progress, args=(
                    consumed, download_size, download_size_list.__len__(), err_file, succeed_file, list_pid, queue))
                # cons.daemon = True
                show_progres.start()
                list_pid.append(show_progres.pid)
            multiprocessing_daemon(multiprocessing, queue, list_pid, download_file_consumer, download_record_dict,
                                   download_record_f, lock, consumed, err_file, succeed_file, print_location)
            queue.join()
            # 等待进度条信息同步
            time.sleep(2)

            for i in list_pid:
                os.kill(i, 9)
        print()
    print('This task took %s\t\t%s/s' % (
        parse_time(time.time() - start_time), parse_size(download_size / (time.time() - start_time))))

    # 确定完整性
    if OSTYPE == 'windows':
        download_record_f = to_zhcn(download_record_f)
        import io
        if os.path.isfile(download_record_f):
            with io.open(download_record_f, 'r', encoding='windows-1252') as f:
                download_record_dict = json.load(f)
    else:
        if os.path.isfile(download_record_f):
            with open(download_record_f, 'r') as f:
                download_record_dict = json.load(f)
    for i in download_record_dict:
        if download_record_dict[i]['status'] == 2:
            if OSTYPE == 'windows':
                name = (to_zhcn(download_record_dict[i]['name'])).encode('utf-8')
            else:
                name = download_record_dict[i]['name']
            download_name_list.remove(name)
    if len(download_name_list) == 0:
        if os.path.isfile(download_record_f):
            os.remove(download_record_f)
    else:
        for i in download_name_list:
            print('Error file %s' % i)


@set_config
def sh(args):
    import readline
    path_matches = []
    res = find_files('/', multiLevel=True, carry=False)
    for i in res:
        path_matches.append(i['filePath'] + i['name'] + '/')
    try:
        import rlcompleter
        readline.parse_and_bind("tab: complete")

        readline.set_completer_delims("")
        bocompleter = BOCompleter(path_matches)
        readline.set_completer(bocompleter.complete)
    except:
        pass
    while True:
        try:
            prompt = '> '
            pwd_str = (config.current_project_name + ':' + config.current_wd)
            if pwd_str is not None:
                prompt = pwd_str + prompt
            sys.stdout.write(to_zhcn(prompt))
            cmd = raw_input()
        except EOFError:
            print("")
            exit(0)
        except KeyboardInterrupt:
            break
        if cmd == '':
            continue
        if cmd == 'exit':
            break
        try:
            if OSTYPE == "windows":
                sys.argv[1:] = [word for word in ((to_zhcn(cmd)).encode('utf-8')).split(' ') if word != '' and ' ']
            else:
                sys.argv[1:] = [word for word in (cmd.encode('utf-8')).split(' ') if word != '' and ' ']
            args = scripts.bo.parser.parse_args(sys.argv[1:])
            args.func(args)
            if hasattr(args, 'command') and args.command == 'select':
                path_matches = []
                res = find_files('/', multiLevel=True, carry=False)
                for i in res:
                    path_matches.append(i['filePath'] + i['name'] + '/')
                try:
                    import rlcompleter
                    readline.parse_and_bind("tab: complete")

                    readline.set_completer_delims("")
                    bocompleter = BOCompleter(path_matches)
                    readline.set_completer(bocompleter.complete)
                except:
                    pass
        except StopIteration:
            exit(0)
        except BaseException as details:
            if not isinstance(details, SystemExit):
                print(str(details) + '\n')


@set_config
def find_data(args):
    project_id = None
    if args.path is None:
        path = get_fully_path("", is_end=False)
    else:
        project_id, path = split_project_path(args.path)

    if path != '/' and path[-1] is '/':
        path = path[0:-1]

    projects = find_files(path, id_or_name=args.name, multiLevel=True,
                          fuzzy_match=True, project_id=project_id)
    if len(args.metadata) != 0:
        metadata = ''
        file_list = []
        for i in args.metadata:
            metadata = i + " " + metadata
        meta_data = dict([i.split("=") for i in metadata.split()])
        for p in projects:
            if p['isFolder'] == '0' or p['isFolder'] == 0:
                if p.get('meta') is None or len(
                        set(meta_data.keys()).difference(p.get('meta')[0].keys())) != 0 or len(
                    set(meta_data.values()).difference(p.get('meta')[0].values())) != 0:
                    continue
                file_list.append(p)
        projects = file_list
    if len(projects) == 0:
        return
    file_status = {
        1: BOLD(RED('Uploading')),
        2: BOLD(GREEN('Available')),
        4: BOLD(RED('Fail')),
        8: 'Connecting',
        16: BOLD(BLUE('Freeze')),
        32: 'Hot',
        64: 'Eeb'
    }
    td = ['status', 'size', 'filePath', 'id']
    table = prettytable.PrettyTable(td, padding_width=1, align='l', vertical_char=' ', junction_char='-')
    for i in td:
        table.align[i] = "l"
    for p in projects:
        if p['isFolder'] == '0' or p['isFolder'] == 0:
            row = []
            for i in td:
                if i == 'size':
                    row.append(to_zhcn(parse_size(p[i], format=False, format_int=2)))
                elif i == 'filePath':
                    row.append((((p[i] + p['name']))))
                elif i == 'status':
                    row.append(file_status.get(int(to_zhcn(p[i]))))
                else:
                    row.append(to_zhcn(p[i]))
            table.add_row(row)
    print(table)


@set_config
def find_job(args):
    status_text = {
        0: BOLD(RED("Unknown")),
        1: BOLD(GREEN("Running")),
        2: BOLD(BLUE("Finished")),
        4: BOLD(YELLOW("Stopped")),
        8: BOLD(RED("Error")),
        16: BOLD(GREEN("Pending"))
    }

    try:
        res = bgionline.api.get_project_job(args.project or config.current_project_id)
        if res == []:
            return 0
        td = ['status', 'name', 'startTime', 'stopTime', 'author']
        table = prettytable.PrettyTable(td, padding_width=1, align='l', vertical_char=' ', junction_char='-')
        for i in td:
            table.align[i] = "l"
        for p in res:
            row = []
            for i in td:
                if i == 'name':
                    row.append((to_zhcn((p[i]))))
                elif i == 'startTime':
                    row.append(format_time(p[i]))
                elif i == 'stopTime':
                    row.append(format_time(p[i]))
                elif i == 'author':
                    row.append(to_zhcn(p['starterId']))
                else:
                    row.append(status_text[p[i]])
            table.add_row(row)

        print(table)

    except Exception as e:
        err_exit(e)


@set_config
def find_app(args):
    status_text = {
        0: BOLD(GREEN("Normal")),
        1: BOLD(YELLOW("Active")),
        2: BOLD(BLUE("Release")),
        4: BOLD(RED("Disabled")),
    }

    try:
        res = bgionline.api.get_project_app(args.project or config.current_project_id)
        if res == []:
            return 0
        td = ['status', 'name', 'author', 'version', 'lastUpdate']
        table = prettytable.PrettyTable(td, padding_width=1, align='l', vertical_char=' ', junction_char='-')
        for i in td:
            table.align[i] = "l"
        for p in res:
            row = []
            for i in td:
                if i == 'name':
                    row.append(((p[i])))
                elif i == 'lastUpdate':
                    row.append(format_time(p[i]))
                elif i == 'version':
                    row.append(to_zhcn(p[i]))
                elif i == 'author':
                    row.append(to_zhcn(p['authorId']))
                elif i == 'status':
                    row.append(status_text[p[i]])
            table.add_row(row)

        print(table)

    except Exception as e:
        err_exit(e)


@set_config
def find_project(args):
    try:
        projects = _list_user_projects(config.username)
    except Exception as e:
        print("Error when listing projects")
        err_exit(e)
    td = ['name', 'owner', 'id']
    table = prettytable.PrettyTable(td, padding_width=1, align='l', vertical_char=' ', junction_char='-')
    for i in td:
        table.align[i] = "l"
    for p in projects:
        row = []
        for i in td:
            if i == 'name':
                row.append(to_zhcn((p[i])))
            elif i == 'owner':
                row.append(to_zhcn(p['ownerId']))
            elif i == 'id':
                row.append(p[i])
        table.add_row(row)

    print(table)


@set_config
def transfer(args):
    try:
        data = {'username': args.username}
        if args.remain:
            data['privilege'] = 4
        project_id = args.project or config.current_project_id
        bgionline.api.transfer(project_id, input_params=data)
    except Exception as e:
        err_exit(e)


@set_config
def whoami(args):
    print('user:%s \nproject:%s[%s]' % (
        config.username, config.current_project_name, config.current_project_id))
