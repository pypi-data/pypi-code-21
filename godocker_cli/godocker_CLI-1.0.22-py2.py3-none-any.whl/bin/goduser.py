#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

from datetime import datetime, timedelta
from os.path import expanduser
import os.path
import sys
from terminaltables import SingleTable
from textwrap import wrap

import click
import requests, json

import xml.etree.ElementTree as ET
import xml.dom.minidom as xmldom

from godockercli.auth import Auth
from godockercli.utils import Utils
from godockercli.httputils import HttpUtils

def print_user_details_tables(user, login):
    """ print user infos """
    #general infos table
    user_infos = user.json()

    user_data = []
    user_data.append(['login', 'api key', 'email', 'admin', 'home directory','uid','gid'])
    user_data.append([user_infos['id'], user_infos['credentials']['apikey'], user_infos['email'], str(user_infos['admin']), user_infos['homeDirectory'], str(user_infos['uid']), str(user_infos['gid'])])

    # general table
    table_general = SingleTable(user_data, "user informations")
    print("\n"+table_general.table+"\n")


    # quota table
    # for old user compatibility. TODO : remove test for production env
    if 'quota_ram' in user_infos['usage']:
        data_quota = []
        data_quota.append(['ram', 'cpu', 'time', 'priority'])
        data_quota.append([str(user_infos['usage']['quota_ram']), str(user_infos['usage']['quota_cpu']), str(user_infos['usage']['quota_time']), str(user_infos['usage']['prio'])])
        table_quota = SingleTable(data_quota, "quotas")
        print("\n"+table_quota.table+"\n")

    # project table
    projects = HttpUtils.http_get_request("/api/1.0/user/"+login+"/project", Auth.server, {'Authorization':'Bearer '+Auth.token}, Auth.noCert)
    projects_info=[]
    projects_info.append(['id', 'description', 'priority'])

    for project in projects.json():
        if project["id"] == "default":
            projects_info.append(
                [str(project['id']), " ", str(project['prio'])]
            )
        else:
            projects_info.append(
                [
                    str(project['id']),
                    str(project['description'])[:15],
                    str(project['prio'])
                ]
            )

    table_projects = SingleTable(projects_info, "user projects")
    print("\n"+table_projects.table+"\n")

    #usage table
    usage = HttpUtils.http_get_request("/api/1.0/user/"+login+"/usage", Auth.server, {'Authorization':'Bearer '+Auth.token}, Auth.noCert)

    table_usage = Utils.get_usage_table(usage)

    print("\n"+table_usage.table+"\n")

    # ssh key table
    table_ssh_key = SingleTable([['']], 'SSH key')
    max_width = table_ssh_key.column_max_width(0)

    if user_infos['credentials']['public'] != "":
        wrapped_string = '\n'.join(wrap(str(user_infos['credentials']['public']), max_width))
    else:
        wrapped_string = "not available"

    table_ssh_key.table_data[0][0] = wrapped_string
    print("\n"+table_ssh_key.table+"\n")


@click.group()
def run():
    pass


@click.command()
@click.option('--xml', '-x', is_flag=True, help="print in xml format")
@click.argument("login", type=str, default="")
def show(login, xml):
    """get user informations"""

    Auth.authenticate()

    if login == "":
        login = Auth.login

    user = HttpUtils.http_get_request("/api/1.0/user/"+login, Auth.server, {'Authorization':'Bearer '+Auth.token}, Auth.noCert)

    if not xml:
        print_user_details_tables(user, login) 
    else:
        Utils.get_user_details_xml(user, login)

@click.option('--xml', '-x', is_flag=True, help="print in xml format")
@click.command("list")
def listuser(xml):
    """get user list (only for administrators)"""
    Auth.authenticate()

    users = HttpUtils.http_get_request("/api/1.0/user", Auth.server, {'Authorization':'Bearer '+Auth.token}, Auth.noCert)

    #general infos table
    users_infos = users.json()

    if xml:
        users = ET.Element("users")
        for user_infos in users_infos:
            single_user = ET.SubElement(users, "user")
            ET.SubElement(single_user, "login").text = user_infos['id']
            ET.SubElement(single_user, "api_key").text = user_infos['credentials']['apikey']
            ET.SubElement(single_user, "email").text = user_infos['email']
            ET.SubElement(single_user, "home_directory").text = user_infos['homeDirectory']

        tree = ET.ElementTree(users)
        tree.write("/tmp/.users.xml")
        xml = xmldom.parse("/tmp/.users.xml").toprettyxml()

        # write in a final xml (pretty)
        xmlfile = open("users_result.xml", 'w')
        xmlfile.write(xml)
        xmlfile.close()
    
        print("Results are available in users_result.xml file")


    else:

        user_data = []
        user_data.append(['login', 'api key', 'email', 'home directory'])

        for user_infos in users_infos:

            user_data.append([user_infos['id'], user_infos['credentials']['apikey'], user_infos['email'], user_infos['homeDirectory']])

        table = SingleTable(user_data)
        table.title = "user(s) informations"

        print("\n"+table.table+"\n")

@click.command()
@click.argument("login", type=str, required="True")
@click.option('--quota_cpu', '-c', type=int, help="number of CPU")
@click.option('--quota_ram', '-r', type=int, help="RAM memory (Gb)")
@click.option('--quota_time', '-t', type=float, help="Time")
@click.option('--priority', '-p', type=int, help="Priority")
def update(login, quota_cpu, quota_ram, quota_time, priority):
    """update user quotas (only for administrators)"""
    Auth.authenticate()

    user = HttpUtils.http_get_request("/api/1.0/user/"+login, Auth.server, {'Authorization':'Bearer '+Auth.token}, Auth.noCert)

    user = user.json()

    if priority >= 0:
        user["usage"]["prio"] = priority
    if quota_cpu >= 0:
        user["usage"]["quota_cpu"] = quota_cpu
    if quota_ram >= 0:
        user["usage"]["quota_ram"] = quota_ram
    if quota_time >= 0:
        user["usage"]["quota_time"] = quota_time

    result_submit = HttpUtils.http_put_request(
        "/api/1.0/user/"+login, json.dumps(user),
        Auth.server,
        {'Authorization':'Bearer '+Auth.token, 'Content-type': 'application/json', 'Accept':'application/json'},
        Auth.noCert
    )

    print("user "+login+" was updated")


# add commands to gojob
run.add_command(show)
run.add_command(listuser)
run.add_command(update)


if __name__ == "__main__":
    run()
