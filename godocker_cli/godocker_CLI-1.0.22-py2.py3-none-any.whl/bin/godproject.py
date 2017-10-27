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


@click.group()
def run():
    pass

@click.command()
@click.argument("project_id", required=True, type=str)
def show(project_id):
    """get project informations"""

    Auth.authenticate()

    if project_id == "default":
        print("No details available for this project")
        sys.exit(0)

    admin = Utils.get_userInfos(Auth.login)['admin']

    if admin:

        project = HttpUtils.http_get_request("/api/1.0/project/"+project_id, Auth.server, {'Authorization':'Bearer '+Auth.token}, Auth.noCert)

        # members
        project = project.json()

        table_info, table_members, table_quota, table_volumes = Utils.get_project_tables(project)

        print("\n"+table_info.table+"\n")
        print("\n"+table_members.table+"\n")
        print("\n"+table_quota.table+"\n")
        print("\n"+table_volumes.table+"\n")



    else:
        projects = HttpUtils.http_get_request("/api/1.0/user/"+Auth.login+"/project", Auth.server, {'Authorization':'Bearer '+Auth.token}, Auth.noCert)
        projects = projects.json()
        find = False
        for project in projects:
            if project_id == project["id"]:
                find = True
                table_info, table_members, table_quota, table_volumes = Utils.get_project_tables(project)
        if not find:
            print("Project does not exist")
            sys.exit(0)
        else :
            print("\n"+table_info.table+"\n")
            print("\n"+table_members.table+"\n")
            print("\n"+table_quota.table+"\n")
            print("\n"+table_volumes.table+"\n")

    # print usage
    usage = HttpUtils.http_get_request("/api/1.0/project/"+project_id+"/usage", Auth.server, {'Authorization':'Bearer '+Auth.token}, Auth.noCert)
    table_usage = Utils.get_usage_table(usage)

    print("\n"+table_usage.table+"\n")

@click.option('--xml', '-x', is_flag=True, help="print in xml format")
@click.option('--login', '-l', type=str, default="", help="user login")
@click.command('list')
def listprojects(login, xml):
    """get user projects list"""
    Auth.authenticate()

    # login
    if login == "":
        login = Auth.login

    projects = HttpUtils.http_get_request("/api/1.0/user/"+login+"/project", Auth.server, {'Authorization':'Bearer '+Auth.token}, Auth.noCert)

    # if xml, write in a xml file
    if xml:
        projects_list = ET.Element("projects")
        for project in projects.json():
            single_project = ET.SubElement(projects_list, "project")
            ET.SubElement(single_project, "id").text = str(project['id'])
            if not project["id"] == "default":
                ET.SubElement(single_project, "description").text = str(project['description'])
            else:
                ET.SubElement(single_project, "description").text = ""
            ET.SubElement(single_project, "priority").text = str(project['prio'])

        tree = ET.ElementTree(projects_list)
        tree.write("/tmp/.projects.xml")
        xml = xmldom.parse("/tmp/.projects.xml").toprettyxml()

        # write in a final xml (pretty)
        xmlfile = open("projects_result.xml", 'w')
        xmlfile.write(xml)
        xmlfile.close()

        print("Results are available in projects_result.xml file")

    else:

        projects_info=[]
        projects_info.append(['id', 'description', 'priority'])

        for project in projects.json():
            if not project["id"] == "default":
                projects_info.append(
                    [
                        str(project['id']),
                        str(project['description'])[:20],
                        str(project['prio'])
                    ]
                )
            else:
                projects_info.append(
                    [
                        str(project['id']),
                        " ",
                        str(project['prio'])
                    ]
                )

        table_projects = SingleTable(projects_info, "user projects")
        print("\n"+table_projects.table+"\n")



@click.command('listall')
def listallprojects():
    """get all projects list (admin only) """
    Auth.authenticate()

    projects = HttpUtils.http_get_request("/api/1.0/project", Auth.server, {'Authorization':'Bearer '+Auth.token}, Auth.noCert)

    projects_info=[]
    projects_info.append(['id', 'description', 'priority'])

    for project in projects.json():
        if not project["id"] == "default":
            projects_info.append(
                [
                    str(project['id']),
                    str(project['description'])[:15],
                    str(project['prio'])
                ]
            )

    table_projects = SingleTable(projects_info, "user projects")
    print("\n"+table_projects.table+"\n")


@click.command()
@click.option('--name', '-n', type=str, required=True, help="project name")
@click.option('--description', '-d', type=str, default="", help="project description")
@click.option('--priority', '-p', type=int, default=50, help="priority")
@click.option('--quota_cpu', '-c', type=int, default=0, help="CPU quota")
@click.option('--quota_ram', '-r', type=int, default=0, help="RAM quota (Gb)")
@click.option('--quota_time', '-t', type=int, default=0, help="time quota")
@click.option('--members', '-m', type=str, default=[], help="members (separated by comma)")
def create(name, description, priority, quota_cpu, quota_ram, quota_time, members):
    """ create a new project (admin only)"""

    Auth.authenticate()

    if not members == []:
        members = members.split(",")

    project = {
        "members": members,
        "prio": priority,
        "quota_cpu": quota_cpu,
        "quota_ram": quota_ram,
        "quota_time": quota_time,
        "id": name,
        "description": description
    }


    result_submit = HttpUtils.http_post_request(
        "/api/1.0/project", json.dumps(project),
        Auth.server,
        {'Authorization':'Bearer '+Auth.token, 'Content-type': 'application/json', 'Accept':'application/json'},
        Auth.noCert
    )

    print("project "+name+" was created")
    #print str(result_submit.json()['msg'])+". Job id is "+str(result_submit.json()['id'])


@click.command()
@click.argument("project", nargs=1, required=True, type=str)
def delete(project):
    """delete a project (admin only)"""

    Auth.authenticate()

    # check if project exists
    project_request = HttpUtils.http_get_request("/api/1.0/project/"+project, Auth.server, {'Authorization':'Bearer '+Auth.token}, Auth.noCert)

    # delete the project
    HttpUtils.http_delete_request("/api/1.0/project/"+project, Auth.server, {'Authorization':'Bearer '+Auth.token}, Auth.noCert)
    print("Project "+project+" has been deleted")



@click.command()
@click.argument("project", nargs=1, required=True, type=str)
@click.option('--add', '-a', is_flag=True, help="Add a volume")
@click.option('--rm', '-r', is_flag=True, help="Remove a volume")
@click.option('--name', '-n', required=True, type=str, help="Volume name")
@click.option('--path', '-p', type=str, help="local path")
@click.option('--mount', '-c', type=str, help="path in container, default: path")
@click.option('--mode', '-m', type=str, help="access (ro/rw), default: ro")
def volume(project, add, rm, name, path, mount, mode):
    """ Add or delete project volumes (admin only)"""
    if not (add or rm):
        print ("Missing command: add or rm")
        sys.exit(1)

    Auth.authenticate()

    # check if project exists
    project_request = HttpUtils.http_get_request("/api/1.0/project/"+project, Auth.server, {'Authorization':'Bearer '+Auth.token}, Auth.noCert)

    project_request = project_request.json()


    if add:
        if mount is None:
            mount = path
        if mode is None:
            mode = 'ro'
        volume = { 'name': name, 'path': path, 'mount': mount, 'acl': mode}
        project_request['volumes'].append(volume)
    if rm:
        # Delete volume
        volumes = [ vol for vol in project_request['volumes'] if vol['name']!= name ]
        project_request['volumes'] = volumes


    result_submit = HttpUtils.http_post_request(
        "/api/1.0/project/"+project, json.dumps(project_request),
        Auth.server,
        {'Authorization':'Bearer '+Auth.token, 'Content-type': 'application/json', 'Accept':'application/json'},
        Auth.noCert
    )

    print("project "+project+" was updated")

    return

@click.command()
@click.argument("project", nargs=1, required=True, type=str)
@click.option('--description', '-d', type=str, help="project description")
@click.option('--priority', '-p', type=int, help="project priority")
@click.option('--quota_cpu', '-c', type=int, help="CPU quota")
@click.option('--quota_ram', '-r', type=int, help="RAM quota (Gb)")
@click.option('--quota_time', '-t', type=int, help="time quota")
def update(project, description, priority, quota_cpu, quota_ram, quota_time):
    """ update project infos or quotas (admin only)"""

    Auth.authenticate()

    # check if project exists
    project_request = HttpUtils.http_get_request("/api/1.0/project/"+project, Auth.server, {'Authorization':'Bearer '+Auth.token}, Auth.noCert)


    project_request = project_request.json()

    members = project_request["members"]
    name = project_request["id"]

    if description >= 0:
        project_request["description"] = description
    if priority >= 0:
        project_request["prio"] = priority
    if quota_cpu >= 0:
        project_request["quota_cpu"] = quota_cpu
    if quota_ram >= 0:
        project_request["quota_ram"] = quota_ram
    if quota_time >= 0:
        project_request["quota_time"] = quota_time

    result_submit = HttpUtils.http_post_request(
        "/api/1.0/project/"+project, json.dumps(project_request),
        Auth.server,
        {'Authorization':'Bearer '+Auth.token, 'Content-type': 'application/json', 'Accept':'application/json'},
        Auth.noCert
    )

    print("project "+project+" was updated")

@click.command()
@click.argument("project", nargs=1, required=True, type=str)
@click.argument("members", nargs=-1, required=True, type=str)
def addmember(project, members):
    """ add members to a project (admin only)"""

    Auth.authenticate()

    # check if project exists
    project_request = HttpUtils.http_get_request("/api/1.0/project/"+project, Auth.server, {'Authorization':'Bearer '+Auth.token}, Auth.noCert)


    project_request = project_request.json()

    # test and add members
    members_array = list(set(members))
    members_existing = []

    for member in members_array:
        if member in project_request["members"]:
            print('WARNING: user '+ member + ' is already in this project')
            members_existing.append(member)

    for member in members_existing:
        members_array.remove(member)

    if members_array:
        project_request["members"].extend(members_array)

        # post the update json
        result_submit = HttpUtils.http_post_request(
            "/api/1.0/project/"+project, json.dumps(project_request),
            Auth.server,
            {'Authorization':'Bearer '+Auth.token, 'Content-type': 'application/json', 'Accept':'application/json'},
            Auth.noCert
        )

        print("project "+project+" was updated")
    else:
        print("Nothing to do")


@click.command()
@click.argument("project", nargs=1, required=True, type=str)
@click.argument("members", nargs=-1, required=True, type=str)
def deletemember(project, members):
    """ delete members to a project (admin only)"""

    Auth.authenticate()

    # check if project exists
    project_request = HttpUtils.http_get_request("/api/1.0/project/"+project, Auth.server, {'Authorization':'Bearer '+Auth.token}, Auth.noCert)

    project_request = project_request.json()

    # test and add members
    members_array = list(set(members))
    members_to_remove = []

    # parse the members project list
    for member in members_array:
        if not member in project_request["members"]:
            print('WARNING: user '+ member + ' is not in this project')
        else:
            # add member in remove array
            members_to_remove.append(member)

    if not members_to_remove:
            print("Nothing to do")
    else:
        # remove members in array
        for member in members_to_remove:
            project_request["members"].remove(member)

        # post the update json
        result_submit = HttpUtils.http_post_request(
            "/api/1.0/project/"+project, json.dumps(project_request),
            Auth.server,
            {'Authorization':'Bearer '+Auth.token, 'Content-type': 'application/json', 'Accept':'application/json'},
            Auth.noCert
        )

        print("project "+project+" was updated")

# add commands to gojob
run.add_command(show)
run.add_command(listprojects)
run.add_command(listallprojects)
run.add_command(create)
run.add_command(delete)
run.add_command(update)
run.add_command(addmember)
run.add_command(deletemember)
run.add_command(volume)


if __name__ == "__main__":
    run()
