#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

from datetime import datetime
from os.path import expanduser
import os.path
import sys

import click
import requests, json

from terminaltables import SingleTable
import subprocess

from godockercli.auth import Auth
from godockercli.utils import Utils
from godockercli.httputils import HttpUtils

@click.group()
def run():
    pass

@click.command()
@click.argument("job_id", required=True)
def info(job_id):
    """ get interactive informations for a job """

    Auth.authenticate()

    task = HttpUtils.http_get_request(
        "/api/1.0/task/"+job_id,
        Auth.server,
        {'Authorization':'Bearer '+Auth.token, 'Content-type': 'application/json', 'Accept':'application/json'},
        Auth.noCert
    )

    task = task.json()

    if not task["command"]["interactive"]:
        print("Job is not in interactive mode")
    elif 'date_running' not in task["status"] or task["status"]["primary"] != "running":
        print("job is not running (pending or over)")
    else:
        data_interactive=[]
        data_interactive.append(
            [
                "host",
                "port"
            ]
        )
        data_interactive.append(
            [
                str(task['container']['meta']['Node']['Name']),
                str(" ".join(task['container']['ports']))
            ]
        )
        table_interactive = SingleTable(data_interactive, "interactive")
        print("\n"+table_interactive.table+"\n")

        data_cmd=[]
        data_cmd.append(["ssh "+Auth.login+"@"+str(task['container']['meta']['Node']['Name'])+" -p "+ str(" ".join(task['container']['ports']))])

        table_cmd = SingleTable(data_cmd, "command line")
        print("\n"+table_cmd.table+"\n")


@click.command()
@click.argument("job_id", required=True)
def connect(job_id):
    """ SSH connection to the container interactive job """

    Auth.authenticate()

    task = HttpUtils.http_get_request(
        "/api/1.0/task/"+job_id,
        Auth.server,
        {'Authorization':'Bearer '+Auth.token, 'Content-type': 'application/json', 'Accept':'application/json'},
        Auth.noCert
    )


    task = task.json()

    if not task["command"]["interactive"]:
        print("Job is not in interactive mode")
    elif 'date_running' not in task["status"] or task["status"]["primary"] != "running":
        print("job is not running (pending or over)")
    else:
        cmd_line=[]
        cmd_line.extend(["ssh", Auth.login+"@"+str(task['container']['meta']['Node']['Name']), "-p", str(" ".join(task['container']['ports']))])
        #cmd_line.extend(["ssh", Auth.login+"@"+"192.168.2.78", "-p", str(" ".join(task['container']['ports']))])

        print("An interactive session is requested\nCommand line : "+" ".join(cmd_line)+"\n")
        os.system(" ".join(cmd_line))


run.add_command(info)
run.add_command(connect)


if __name__ == "__main__":
    run()
