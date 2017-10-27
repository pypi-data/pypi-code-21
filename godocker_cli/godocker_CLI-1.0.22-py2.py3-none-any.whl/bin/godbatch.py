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
import sqlite3
import logging
import uuid
from terminaltables import SingleTable

from godockercli.auth import Auth
from godockercli.utils import Utils
from godockercli.httputils import HttpUtils

import signal
import sys


USER_STOP = False

def signal_handler(signal, frame):
    global USER_STOP
    print('Interruption requested, stopping.....')
    USER_STOP = True

signal.signal(signal.SIGINT, signal_handler)

MAX_JOBS = 2

@click.group()
def run():
    pass

@click.command()
@click.option('--batch', type=str, default="default", help="Batch list name")
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
@click.option('--label', '-l', type=str, multiple=True, default="", help="Label constraints")
@click.option('--interactive', is_flag=True, help="interactive mode for ssh connection")
@click.option('--root', is_flag=True, help="root mode")
@click.option('--login', type=str, default="", help="user login")
@click.option('--reloadconfig', is_flag=True, help="reload configuration from server")
def add(batch, name, description, tags, project, cpu, ram, image, external_image, script, interactive, root, volume, array, login, label, reloadconfig):
    """ Add a job to batch list"""
    conn = sqlite3.connect('godbatch.db')
    batch_cursor = conn.cursor()
    # Create table
    batch_cursor.execute('''CREATE TABLE IF NOT EXISTS godbatch
             (id long, batchlist text, task text, status int, job_id long)''')

    batch_cursor.execute('''CREATE TABLE IF NOT EXISTS godconfig
             (id long, config text)''')

    has_config = False

    for row in batch_cursor.execute('SELECT * FROM godconfig WHERE id=1'):
        has_config = True
        config = json.loads(row[1])

    if not has_config:
        config = {
            'labels': Utils.get_contraint_labels(),
            'images': Utils.get_docker_images_url(),
            'interactive_images': Utils.get_docker_images_url_interactive()
        }
        batch_cursor.execute("INSERT INTO godconfig VALUES (?, ?)" , (1, json.dumps(config)))
    else:
        if reloadconfig:
            config = {
                'labels': Utils.get_contraint_labels(),
                'images': Utils.get_docker_images_url(),
                'interactive_images': Utils.get_docker_images_url_interactive()
            }
            batch_cursor.execute("UPDATE godconfig SET config=? WHERE id=1" , (json.dumps(config),))


    available_labels = config['labels']
    docker_images = config['images']
    docker_interactive_images = config['interactive_images']

    # manage constraints
    for user_label in list(label):
        if user_label not in available_labels:
            print("Constraint '"+user_label+" does not exist. Please choose in the list below:")
            for available_label in available_labels:
                print("   "+available_label)
            sys.exit(1)

    if tags:
        tags += ',batch:' + batch
    else:
        tags = 'batch:'+batch

    # test image selection
    if not image in docker_images and not external_image:
        print("Wrong image url selected. Please launch 'godimage list' to check your image url or use the --external_image.")
        sys.exit(0)

    if (not script and not interactive) or (script and interactive):
        print("You must use either --script or --interactive option")
        sys.exit(0)

    if interactive:
        if image not in docker_interactive_images:
            print("You are not allowed to use this image with interactive mode. Please launch 'godimage list' to check your image url")
            sys.exit(0)

    command = ''

    if script:
        command=script.read()

    task = {
     'name': name,
     'description': description,
     'tags': tags,
     'project': project,
     'cpu': cpu,
     'ram': ram,
     'image': image,
     'external_image': external_image,
     'command': command,
     'interactive': interactive,
     'root': root,
     'volume': volume,
     'array': array,
     'login': login,
     'label': label
    }
    json_task = json.dumps(task)
    # Insert a row of data
    batch_id = uuid.uuid1().hex
    batch_cursor.execute("INSERT INTO godbatch VALUES (?, ?, ?, ?, ?)" , (batch_id, batch, json_task, 0, -1))
    conn.commit()
    conn.close()

@click.command()
def show():
    """ Show status of batch lists"""
    conn = None
    try:
        conn = sqlite3.connect('godbatch.db')
        batch_cursor = conn.cursor()
        table_data = []
        table_data.append(
            ['list',
            'task',
            'status',
            'job_id']
        )
        for row in batch_cursor.execute('SELECT * FROM godbatch ORDER BY batchlist'):
            task = json.loads(row[2])
            table_data.append([row[1], task['name'] + ':' + task['description'], str(row[3]), str(row[4])])

        print(SingleTable(table_data).table)
    except Exception as e:
        print('Show:Database error: ' + str(e))
    if conn is not None:
        conn.close()


@click.command()
@click.option('--batch', type=str, default="all", help="Delete batch list elements, defaults to all")
def clean(batch):
    """ Clear a batch list"""
    conn = None
    try:
        conn = sqlite3.connect('godbatch.db')
        batch_cursor = conn.cursor()
        if batch == 'all':
            batch_cursor.execute('DELETE FROM godbatch')
        else:
            batch_cursor.execute('DELETE FROM godbatch WHERE batchlist=?', (batch))
        conn.commit()
    except Exception as e:
        print('Database does not exist, no batch list created')
    if conn is not None:
        conn.close()

def jobs_per_batch():
    '''
    Get number of running/pending jobs per batch list
    '''
    #Auth.authenticate()
    tasks = HttpUtils.http_get_request(
        "/api/1.0/task/active",
        Auth.server,
        {'Authorization':'Bearer '+Auth.token},
        Auth.noCert
    )
    result=tasks.json()
    nbjobs = {}
    for task in result:
        if 'tags' in task['meta']:
            for tag in task['meta']['tags']:
                if tag.startswith('batch:'):
                    batchlist = tag.replace('batch:','')
                    if batchlist not in nbjobs:
                        nbjobs[batchlist] = 0
                    nbjobs[batchlist] += 1
    return nbjobs

@click.command()
@click.option('--batch', type=str, default='default', help="Batch list to cancel, defaults to 'default'")
def cancel(batch):
    """Cancel a play command on a batch list"""
    conn = None
    try:
        conn = sqlite3.connect('godbatch.db')
        batch_cursor = conn.cursor()
        batch_cursor.execute('UPDATE godbatch SET status=? WHERE status=0 AND batchlist=?', (3, batch))
        conn.commit()
    except Exception as e:
        print('Cancel:Database error:' + str(e))
    if conn is not None:
        conn.close()
    print("Batch execution cancelled, will stop sending new jobs")


def run_task(task, user_infos):
    name = task['name']
    description = task['description']
    tags = task['tags']
    project = task['project']
    cpu = task['cpu']
    ram = task['ram']
    image = task['image']
    external_image = task['external_image']
    command = task['command']
    interactive = task['interactive']
    root = task['root']
    volume = task['volume']
    array = task['array']
    login = task['login']
    label = task['label']

    # manage volumes
    volumes=[]
    for volume in list(volume):
        acl = Utils.get_acl_for_volume(volume)
        volumes.append({'name': volume, 'acl': str(acl)})
    # manage constraints
    labels = list(label)


    #tags
    tags_tab = tags.split(",")

    # login
    if login == "":
        login = Auth.login

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
            'array': { 'values': array},
            'label': labels
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
    result_submit = HttpUtils.http_post_request(
        "/api/1.0/task", json.dumps(job),
        Auth.server,
        {'Authorization':'Bearer '+Auth.token, 'Content-type': 'application/json', 'Accept':'application/json'},
        Auth.noCert
    )
    result_json = result_submit.json()
    return result_json['id']

@click.command()
@click.option('--parallel', type=int, default=100, help="Max number of parallel jobs")
@click.option('--batch', type=str, default='default', help="Batch list to play, defaults to 'default'")
def play(parallel, batch):
    """Play command on a batch list, parallelizing task submission"""

    global USER_STOP
    conn = None
    try:
        conn = sqlite3.connect('godbatch.db')
        batch_cursor = conn.cursor()
        no_row = False
        Auth.authenticate()
        user_infos = None
        while not no_row and not USER_STOP:
            no_row = True
            nbjobs = jobs_per_batch()
            for row in batch_cursor.execute('SELECT * FROM godbatch WHERE status=0 AND batchlist=?',(batch,)):
                no_row = False
                if batch in nbjobs and nbjobs[batch] >= parallel:
                    break
                if batch not in nbjobs:
                    nbjobs[batch] = 0
                nbjobs[batch] += 1
                task = json.loads(row[2])

                if user_infos is None:
                    login = task['login']
                    if login == "":
                        login = Auth.login
                    user_infos = Utils.get_userInfos(login)

                job_id = run_task(task, user_infos)

                #print('SHOULD PLAY: '+str(row))
                batch_cursor.execute('UPDATE godbatch SET status=?, job_id=? WHERE id=?', (1, job_id, row[0]))
            conn.commit()
            if not no_row:
                time.sleep(2)
    except Exception as e:
        print('Play:Database error:' + str(e))
    if conn is not None:
        conn.close()
    if not USER_STOP:
        print("Completed!")
    else:
        print("Batch execution interrupted")

run.add_command(add)
run.add_command(show)
run.add_command(play)
run.add_command(cancel)
run.add_command(clean)

if __name__ == "__main__":
    run()
