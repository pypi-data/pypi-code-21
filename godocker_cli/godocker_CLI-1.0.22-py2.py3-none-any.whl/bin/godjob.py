#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

from datetime import datetime
import time

import click
import requests, json
import sys, os
from terminaltables import SingleTable
from os.path import expanduser
from operator import itemgetter
from string import Template

from godockercli.auth import Auth
from godockercli.utils import Utils
from godockercli.httputils import HttpUtils

def print_task_infos_tables(job, tags):
    """ print job infos """
    #data_id
    data_id = []
    data_id.append(
        [
            "id",
            "name",
            "description",
            "tags",
            "root",
            "interactive"
        ]
    )
    data_id.append(
        [
            str(job["id"]),
            str(job["meta"]["name"]),
            str(job['meta']["description"].encode('utf-8'))[:20],
            tags,
            str(job['container']['root']),
            str(job['command']['interactive'])
        ]
    )

    # tasks dependency
    if 'tasks' in job['requirements']:
       if job['requirements']['tasks']:
           tasks_dep = []
           task_list = ""
           for task in job['requirements']['tasks']:
               tasks_dep.append(['job ID', str(task)])

           table_tasks_requirement = SingleTable(tasks_dep, 'job parents')
           table_tasks_requirement.inner_heading_row_border = False
       else:
           table_tasks_requirement = None
    else:
        table_tasks_requirement = None

    #data_user
    data_user = []
    data_user.append(
        [
            'login',
            'project'
        ]
    )
    data_user.append(
        [
            str(job['user']['id']),
            str(job['user']['project'])
        ]
    )

    # container
    data_container = []
    data_container.append(
        ['image']
    )
    data_container.append(
        [str(job['container']['image'])]
    )

    # container capacity
    data_capacity =[]
    data_capacity.append(['cpu', 'ram', 'gpus'])
    if 'gpus' not in job['requirements']:
        job['requirements']['gpus'] = 0
    data_capacity.append([str(job['requirements']['cpu']), str(job['requirements']['ram']), str(job['requirements']['gpus'])])

    table_capacity = SingleTable(data_capacity, "capacity")

    # volumes
    data_volumes = []
    data_volumes.append(['name', 'path', 'mount', 'acl'])
    for volume in job['container']['volumes']:
        data_volumes.append([str(volume['name']), str(volume['path']), str(volume['mount']), str(volume['acl'])])
    if 'tmpstorage' in job['requirements'] and job['requirements']['tmpstorage'] is not None:
        data_volumes.append(['tmp-data', str(job['requirements']['tmpstorage']['size']), '/tmp-data', 'rw'])
    table_volumes = SingleTable(data_volumes, "volumes")

    #data_status
    data_status = []

    # test if job was in running state
    if 'date_running' in job["status"]:
        data_status.append(
            [
                'primary_status',
                'secondary_status',
                'exit_code',
                'date_running',
                'date_over'
            ]
        )

        if job["status"]['date_over'] is not None:
            date_over_convert = datetime.fromtimestamp(job["status"]['date_over'])
        else:
            date_over_convert = None
        exit_code = ''
        if 'meta' in job["container"] and 'State' in job["container"]["meta"] and 'ExitCode' in job["container"]["meta"]["State"]:
            exit_code = str(job["container"]["meta"]["State"]["ExitCode"])
        data_status.append(

            [
                str(job["status"]['primary']),
                str(job["status"]['secondary']),
                str(exit_code),
                str(datetime.fromtimestamp(job["status"]['date_running'])),
                str(date_over_convert)

            ]
        )
    else:
        data_status.append(
            [
                'primary_status',
                'secondary_status',
                'date_running',
                'date_over'
            ]
        )

        if job["status"]['date_over'] is not None:
            date_over_convert = datetime.fromtimestamp(job["status"]['date_over'])
        else:
            date_over_convert = None

        data_status.append(

            [
                str(job["status"]['primary']),
                str(job["status"]['secondary']),
                "None",
                str(date_over_convert)
            ]
        )

    table_id = SingleTable(data_id, "job")
    table_user = SingleTable(data_user, "user")
    table_status = SingleTable(data_status, "status")
    table_container = SingleTable(data_container, "container")

    # print table
    print("\n"+table_id.table+"\n")

    #data interactive
    if job['command']['interactive'] and 'date_running' in job["status"] and job["status"]['primary'] == 'running':
        data_interactive=[]
        data_interactive.append(
            [
                "host",
                "port"
            ]
        )
        data_interactive.append(
            [
                str(job['container']['meta']['Node']['Name']),
                str(" ".join(job['container']['ports']))
            ]
        )
        table_interactive = SingleTable(data_interactive, "interactive")
        print("\n"+table_interactive.table+"\n")

    # print classic tables
    print("\n"+table_user.table+"\n")
    if table_tasks_requirement:
        print("\n"+table_tasks_requirement.table+"\n")
    print("\n"+table_status.table+"\n")
    print("\n"+table_container.table+"\n")
    print("\n"+table_capacity.table+"\n")
    print("\n"+table_volumes.table+"\n")

@click.group()
def run():
    pass

@click.group('list')
def listjobs():
    """list godocker jobs"""
    pass

@click.option('--skip', '-s', type=int, default=0, help="default : 0")
@click.option('--limit', '-l', type=int, default=100, help="default : 100")
@click.argument('regex', required=False)
@click.option('--all', '-a', is_flag=True, help="print all jobs (last 100 by default)")
@click.option('--xml', '-x', is_flag=True, help="print in xml format")
@click.option('--project', type=str, help="project filter")
@click.command()
def over(skip, limit, regex, xml, all, project):
    """list user over jobs"""

    Auth.authenticate()

    if all:
       limit = 0

    project_filter = ''
    if project:
        project_filter = '?project='+project

    tasks = HttpUtils.http_post_request(
        "/api/1.0/task/over/"+str(skip)+"/"+str(limit)+project_filter,
        {},
        Auth.server,
        {'Authorization':'Bearer '+Auth.token, 'Content-type': 'application/json', 'Accept':'application/json'},
        Auth.noCert
    )

    result=tasks.json()

    if xml:
        Utils.get_list_tasks_xml(result, regex)
    else:
        # print table
        table = Utils.get_list_tasks_table(result, regex)
        table.title = "Over jobs"
        print("\n"+table.table+"\n")

@click.option('--skip', '-s', type=int, default=0, help="default : 0")
@click.option('--limit', '-l', type=int, default=100, help="default : 100")
@click.argument('regex', required=False)
@click.option('--all', '-a', is_flag=True, help="print all jobs (last 100 by default)")
@click.option('--xml', '-x', is_flag=True, help="print in xml format")
@click.command()
def overall(skip, limit, regex, xml, all):
    """list all over jobs (only for administrators)"""

    Auth.authenticate()

    if all:
       limit = 0

    tasks = HttpUtils.http_post_request(
        "/api/1.0/task/over/all/"+str(skip)+"/"+str(limit),
        {},
        Auth.server,
        {'Authorization':'Bearer '+Auth.token, 'Content-type': 'application/json', 'Accept':'application/json'},
        Auth.noCert
    )

    result=tasks.json()


    # get table
    if xml:
        Utils.get_list_tasks_xml(result, regex)
    else:
        table = Utils.get_list_tasks_table(result, regex)
        table.title ="All over jobs"
        print("\n"+table.table+"\n")

@click.option('--xml', '-x', is_flag=True, help="print in xml format")
@click.argument('regex', required=False)
@click.option('--project', type=str, help="project filter")
@click.command()
def active(xml, regex, project):
    """list user active jobs"""

    Auth.authenticate()

    project_filter = ''
    if project:
        project_filter = '?project='+project

    tasks = HttpUtils.http_get_request(
        "/api/1.0/task/active",
        Auth.server,
        {'Authorization':'Bearer '+Auth.token},
        Auth.noCert
    )

    result=tasks.json()

    if xml:
        Utils.get_list_tasks_xml(result, regex)
    else:
        # get table
        table = Utils.get_list_tasks_table(result, regex)
        table.title = "Active jobs"
        print("\n"+table.table+"\n")

@click.option('--xml', '-x', is_flag=True, help="print in xml format")
@click.argument('regex', required=False)
@click.command()
def activeall(xml, regex):
    """list all active jobs (only for administrators)"""

    Auth.authenticate()

    tasks = HttpUtils.http_get_request(
        "/api/1.0/task/active/all",
        Auth.server,
        {'Authorization':'Bearer '+Auth.token},
        Auth.noCert
    )

    result=tasks.json()

    # get table
    if xml:
        Utils.get_list_tasks_xml(result, regex)
    else:
        table = Utils.get_list_tasks_table(result, regex)
        table.title = "Active jobs"
        print("\n"+table.table+"\n")


@click.command()
@click.argument("job_id", type=int, required=True)
@click.option('--xml', '-x', is_flag=True, help="print in xml format")
def show(job_id, xml):
    """show job details"""
    Auth.authenticate()

    task = HttpUtils.http_get_request(
        "/api/1.0/task/"+str(job_id),
        Auth.server,
        {'Authorization':'Bearer '+Auth.token},
        Auth.noCert
    )

    job=task.json()

    tags = ",".join(job['meta']['tags']).encode('utf-8')

    if not xml:
        print_task_infos_tables(job, tags)
    else:
        Utils.get_task_infos_xml(job, tags)

@click.argument("regex", required=True)
@click.command()
def search(regex):
    """search active or over jobs from a regex"""

    Auth.authenticate()

    # over jobs section
    tasks_over = HttpUtils.http_post_request(
        "/api/1.0/task/over/0/0",
        {},
        Auth.server,
        {'Authorization':'Bearer '+Auth.token, 'Content-type': 'application/json', 'Accept':'application/json'},
        Auth.noCert
    )

    result_over=tasks_over.json()

    table = Utils.get_list_tasks_table(result_over, regex)
    table.title ="Over jobs"

    # active jobs section
    tasks_active = HttpUtils.http_get_request(
        "/api/1.0/task/active",
        Auth.server,
        {'Authorization':'Bearer '+Auth.token},
        Auth.noCert
    )

    result_active=tasks_active.json()

    table_active = Utils.get_list_tasks_table(result_active, regex)
    table_active.title ="Running jobs"

    print("\n"+table_active.table+"\n")
    print("\n"+table.table+"\n")


@click.command()
@click.argument("job_id", nargs=-1, required=True, type=int)
def kill(job_id):
    """kill a user active job"""

    Auth.authenticate()

    for id in job_id:

        state = Utils.get_job_infos(id)["status"]
        # if state doesn't allow the kill
        if state["secondary"] == "kill requested":
            print("Job "+str(id)+" is already in kill requested.")
            sys.exit()
        elif state["primary"] == "over":
            print("Job "+str(id)+" is already over. Run 'gojob list running' and check your job id")
        # else kill the job
        else:
            HttpUtils.http_delete_request("/api/1.0/task/"+str(id), Auth.server, {'Authorization':'Bearer '+Auth.token}, Auth.noCert)
            print("Job "+str(id)+" has changed into kill requested")


@click.command()
@click.option('--login', type=str, default=None, help="User login (default to authenticated user)")
@click.option('--tag', '-t', type=str, default=None, help="Matching tag")
def killall(login, tag):
    """kill all active jobs, optionally matching tag"""

    Auth.authenticate()

    if login == None:
        login = Auth.login

    tagfilter = ""
    if tag:
        tagfilter = "?tag="+str(tag)

    HttpUtils.http_delete_request("/api/1.0/user/"+login+"/task" + tagfilter, Auth.server, {'Authorization':'Bearer '+Auth.token}, Auth.noCert)
    print("All "+login+" jobs have been changed into kill requested state")
    if tag:
        print("Jobs filtered with tag: "+tag)

@click.command()
@click.argument("job_id", nargs=-1, type=int, required=True)
def suspend(job_id):
    """suspend an active job"""

    Auth.authenticate()

    for id in job_id:

        job_infos = Utils.get_job_infos(id)

        if "pause" in Utils.get_executor_features():
            # check the state
            state = job_infos["status"]
            if state["secondary"] == "suspended" or \
               state["secondary"] == "suspend requested" or \
               state["secondary"] == "kill requested":
                print("Job "+str(id)+" is in "+state["secondary"]+" state. Run 'gojob list running' and check your job status.")
            elif state["primary"] == "over":
                print("Job "+str(id)+" is over. Run 'gojob list running' and check your job id.")
            # test if is in interactive mode
            elif job_infos['command']['interactive']:
                print("Job "+str(id)+" is an interactive session. You're not allowed to suspend this job.")
            else:
                HttpUtils.http_get_request("/api/1.0/task/"+str(id)+"/suspend", Auth.server, {'Authorization':'Bearer '+Auth.token}, Auth.noCert)
                print("Job "+str(id)+" is now suspended")
        else:
                print("The godocker configuration does not allow suspend action")

@click.command()
@click.argument("job_id", nargs=-1, type=int, required=True)
def resume(job_id):
    """resume a suspended job"""

    Auth.authenticate()

    for id in job_id:

        # check the state
        state = Utils.get_job_infos(id)["status"]
        if state["secondary"] == "resumed" or \
           state["secondary"] == "resumed requested" or \
           state["secondary"] == "kill requested" or \
           state["secondary"] == "suspend requested":
            print("Job "+str(id)+" is in "+str(state["secondary"])+" state. Run 'gojob list running' and check your job id")
        elif state["secondary"] is None:
            print("Job "+str(id)+" is in running state. Run 'gojob list running' and check your job id")
        elif state["primary"] == "over":
            print("Job "+str(id)+" is over. Run 'gojob list running' and check your job id")
        else:
            HttpUtils.http_get_request("/api/1.0/task/"+str(id)+"/resume", Auth.server, {'Authorization':'Bearer '+Auth.token}, Auth.noCert)
            print("Job "+str(id)+" is now resumed")

@click.command()
@click.option('--id', '-i', type=str, required=True, help="Job id")
@click.option('--req', '-r', type=str, required=True, help="Requirement")
@click.option('--value', '-v', type=str, required=True, help="Value")
def update(id, req, value):
    """add a requirement to update in a job"""

    Auth.authenticate()
    update_req = {'name': req, 'value': value}
    result_submit = HttpUtils.http_put_request(
        "/api/1.0/task/"+id, json.dumps(update_req),
        Auth.server,
        {'Authorization':'Bearer '+Auth.token, 'Content-type': 'application/json', 'Accept':'application/json'},
        Auth.noCert
    )
    print(str(result_submit.json()))

@click.command()
@click.option('--id', '-i', type=str, help="Job id")
@click.option('--days', '-d', type=int, help="Number of days")
@click.option('--tag', '-t', type=str, help="Delete jobs contaning tag")
@click.option('--purge', '-p', is_flag=True, help="Delete job, warning: will delete all job info from database")
def archive(id, days, tag, purge):
    """archive a job"""
    if days is None and id is None:
        print("Need id or days to be set")
        sys.exit(1)
    Auth.authenticate()
    result_submit = None
    if days is not None:
        if purge:
            has_tag = ''
            if tag:
                has_tag = '?tag='+str(tag)
            result_submit = HttpUtils.http_delete_request(
                "/api/1.0/archive/" + str(days) + has_tag,
                Auth.server,
                {'Authorization':'Bearer '+Auth.token, 'Content-type': 'application/json', 'Accept':'application/json'},
                Auth.noCert
            )
        else:
            result_submit = HttpUtils.http_get_request(
                "/api/1.0/archive/" + str(days),
                Auth.server,
                {'Authorization':'Bearer '+Auth.token, 'Content-type': 'application/json', 'Accept':'application/json'},
                Auth.noCert
            )
    else:
        if purge:
            result_submit = HttpUtils.http_delete_request(
                "/api/1.0/task/" + id + "/archive",
                Auth.server,
                {'Authorization':'Bearer '+Auth.token, 'Content-type': 'application/json', 'Accept':'application/json'},
                Auth.noCert
            )
        else:
            result_submit = HttpUtils.http_get_request(
                "/api/1.0/task/" + id + "/archive",
                Auth.server,
                {'Authorization':'Bearer '+Auth.token, 'Content-type': 'application/json', 'Accept':'application/json'},
                Auth.noCert
            )
    if result_submit and result_submit.status_code != 200:
        print("Archive failure, got code: "+str(httpresult.status_code))
    else:
        if id:
            print("Job "+id+" archived.")
        else:
            print("Jobs will be archived")


@click.command()
@click.option('--name', '-n', type=str, required=True, help="Job name")
@click.option('--description', '-d', type=str, default="", help="description")
@click.option('--tags', '-t', type=str, default="", help="tags (separated by comma)")
@click.option('--project', '-p', type=click.Choice(Utils.get_projects_for_user()), default="default", help="project name")
@click.option('--cpu', '-c', default=1, help="number of CPU")
@click.option('--ram', '-r', default=1, help="RAM memory (Gb)")
@click.option('--image', '-i', required=True, help="image URL")
@click.option('--external_image', is_flag=True, help="use an external image URL")
@click.option('--script', '-s', type=click.File('rb'), help="bash script only")
@click.option('--volume', '-v', type=click.Choice(Utils.get_volumes_name()), multiple=True, default="", help="volume to mount")
@click.option('--array', '-a', type=str, default=None, help="array : 'start:stop:step'")
@click.option('--label', '-l', type=str, multiple=True, default="", help="label constraints")
@click.option('--interactive', is_flag=True, help="interactive mode for ssh connection")
@click.option('--root', is_flag=True, help="root mode")
@click.option('--login', type=str, default="", help="user login")
@click.option('--parent', type=str, default="", help="job(s) to be finished before running the job (separated by comma)")
@click.option('--tmp_storage', type=str, default="", help="local storage requirements")
@click.option('--env', type=str, default=None, multiple=True, help="Substitute environment variables in script")
@click.option('--cmd', type=str, default=None, help="Command to execute, exclusive with --script")
@click.option('--wait', is_flag=True, help="keep waiting for the end of the job")
@click.option('--retry', default=0, help="Number of retries in case of node failure, default none")
@click.option('--placement', type=str, help="executor placement")
@click.option('--gpus', '-g', default=0, help="number of GPU")
def create(name, description, tags, project, cpu, ram, image, external_image, script, interactive, root, volume, array, login, label, parent, tmp_storage, env, cmd, wait, retry, placement, gpus):
    """ create a new job """

    Auth.authenticate()

    # manage volumes
    volumes=[]
    for user_volume in list(volume):
        acl = Utils.get_acl_for_volume(user_volume)
        volumes.append({'name': user_volume, 'acl': str(acl)})

    # manage constraints
    labels = []
    available_labels = Utils.get_contraint_labels()
    for user_label in list(label):
        if user_label not in available_labels:
            print("Constraint '"+user_label+" does not exist. Please choose in the list below:")
            for available_label in available_labels:
                print("   "+available_label)
            sys.exit(1)
        else:
            labels.append(user_label)


    # test image selection
    if not image in Utils.get_docker_images_url() and not external_image:
        print("Wrong image url selected. Please launch 'godimage list' to check your image url or use the --external_image.")
        sys.exit(1)

    if (not script and not cmd and not interactive):
        print("You must use either --script/--cmd or --interactive option")
        sys.exit(1)

    #if interactive and image not in Utils.get_docker_images_url_interactive():
    #    print("You are not allowed to use this image with interactive mode. Please launch 'godimage list' to check your image url")
    #    sys.exit(0)

    # command
    command = ''
    if script:
        command = script.read()
    if cmd:
        command = cmd

    if env is not None and env:
        template_vars = {}
        for envvar in env:
            if envvar not in os.environ:
                print("Environment variable %s is not defined" % envvar)
                sys.exit(1)
            template_vars[envvar] = os.environ[envvar]
        command = Template(command).safe_substitute(template_vars)

    #tags
    if tags:
        tags_tab = tags.split(",")
    else:
        tags_tab = []

    # manage depends
    tasks_depends = []
    if parent:
        tasks_depends = parent.split(",")

    # login
    if login == "":
        login = Auth.login

    user_infos = Utils.get_userInfos(login)

    dt = datetime.now()

    job = {
        'user' : {
            'id' : user_infos['id'],
            'uid' : user_infos['uid'],
            'gid' : user_infos['gid'],
            'project' : project
        },
        'date': time.mktime(dt.timetuple()),
        'meta': {
            'name': name,
            'description': description,
            'tags': tags_tab
        },
        'requirements': {
            'cpu': cpu,
            # In Gb
            'ram': ram,
            'gpus': gpus,
            'array': { 'values': array},
            'label': labels,
            'failure_policy': int(retry),
	        'tasks': tasks_depends,
            'tmpstorage': None,
            'executor': placement
        },
        'container': {
            'image': str(image),
            'volumes': volumes,
            'network': True,
            'id': None,
            'meta': None,
            'stats': None,
            'ports': [],
            'root': root
        },
        'command': {
            'interactive': interactive,
            'cmd': command,
        },
        'status': {
            'primary': None,
            'secondary': None
        }

    }

    if tmp_storage:
        job['requirements']['tmpstorage']= {'size': tmp_storage, 'path': None}

    result_submit = HttpUtils.http_post_request(
        "/api/1.0/task", json.dumps(job),
        Auth.server,
        {'Authorization':'Bearer '+Auth.token, 'Content-type': 'application/json', 'Accept':'application/json'},
        Auth.noCert
    )
    result_json = result_submit.json()
    if wait:
        is_over = False
        while not is_over:
            is_over = Utils.is_finish(result_json['id'])
            time.sleep(2)
    print(str(result_submit.json()['msg'])+". Job id is "+str(result_json['id']))

# add commands to gojob
run.add_command(listjobs)
run.add_command(show)
listjobs.add_command(active)
listjobs.add_command(over)
listjobs.add_command(activeall)
listjobs.add_command(overall)
run.add_command(kill)
run.add_command(killall)
run.add_command(suspend)
run.add_command(resume)
run.add_command(create)
run.add_command(search)
run.add_command(update)
run.add_command(archive)

if __name__ == "__main__":
    run()
