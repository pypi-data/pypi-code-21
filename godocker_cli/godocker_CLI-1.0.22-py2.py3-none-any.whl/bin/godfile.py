#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

from os.path import expanduser
from terminaltables import SingleTable
import os.path
import sys

import click
import requests, json

from godockercli.auth import Auth
from godockercli.utils import Utils
from godockercli.httputils import HttpUtils

import humanfriendly

@click.group()
def run():
    pass

@click.command()
@click.argument("job_id", nargs=1, required=True, type=int)
@click.argument("directory", nargs=1, type=str, default="")
def list(job_id, directory):
    """ list all files associated with a job"""

    Auth.authenticate()

    files = HttpUtils.http_get_request("/api/1.0/task/"+str(job_id)+"/files/"+directory, Auth.server, {'Authorization':'Bearer '+Auth.token}, Auth.noCert)

    # check if directory or not
    if not files.headers['content-type'] == "application/json; charset=UTF-8":
        print("Thanks to enter a valid directory. Run 'godfile list' and check your directory name.")
    else:
        json_res = files.json()
        files_data = []
        files_data.append(['name', 'type', 'size'])
        for file in json_res:
            file_infos = [
                str(file['name']),
                str(file['type'])
            ]

            if str(file['type']) == "dir":
                file_infos.append("-")
            else:
                # print size in human format
                num_bytes = humanfriendly.parse_size(str(file['size']))
                file_infos.append(humanfriendly.format_size(num_bytes))

            files_data.append(file_infos)

        table_files = SingleTable(files_data, directory)
        print("\n"+table_files.table+"\n")

@click.command()
@click.argument("job_id", nargs=1, required=True, type=int)
@click.argument("file", nargs=1, required=True, type=str, default="god.log")
@click.argument("destination", nargs=1, type=str, default=".")
def download(job_id, file, destination):
    "download file job result only. By default, god.log is download"

    Auth.authenticate()

    # get files infos
    files = HttpUtils.http_get_request("/api/1.0/task/"+str(job_id)+"/files/"+file, Auth.server, {'Authorization':'Bearer '+Auth.token}, Auth.noCert)

    # if result is a json, several files or directory must be downloaded
    if files.headers['content-type'] == "application/json; charset=UTF-8":
        # TOTO
        print("Please enter a file")
    else:
        # rename god.log with job id to avoid erase
        if file == "god.log":
            file = "god_"+str(job_id)+".log"

        # test destination dir
        if not os.path.exists(destination) or not os.path.isdir(destination):
            print(destination+" is not a directory or does not exist")
            sys.exit(1)

        destination_file_path = os.path.normpath(destination+"/"+os.path.basename(file))
        file_result = open(destination_file_path, "w")

        if sys.version_info >= (3,0):
            file_result.write(files.content.decode('utf-8'))
        else:
            file_result.write(files.content)

        file_result.close()
        print(os.path.basename(file)+" file was downloaded in "+destination_file_path+ " file.")


run.add_command(list)
run.add_command(download)


if __name__ == "__main__":
    run()
