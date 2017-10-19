# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 GNS3 Technologies Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import aiohttp
import asyncio
import json
import os
import psutil
import tempfile

from gns3server.web.route import Route
from gns3server.compute.project_manager import ProjectManager
from gns3server.compute import MODULES

from gns3server.schemas.project import (
    PROJECT_OBJECT_SCHEMA,
    PROJECT_CREATE_SCHEMA,
    PROJECT_UPDATE_SCHEMA,
    PROJECT_FILE_LIST_SCHEMA,
    PROJECT_LIST_SCHEMA
)

import logging
log = logging.getLogger()


class ProjectHandler:

    # How many clients have subscribed to notifications
    _notifications_listening = {}

    @Route.get(
        r"/projects",
        description="List all projects opened on the server",
        status_codes={
            200: "Project list",
        },
        output=PROJECT_LIST_SCHEMA
    )
    def list_projects(request, response):

        pm = ProjectManager.instance()
        response.set_status(200)
        response.json(list(pm.projects))

    @Route.post(
        r"/projects",
        description="Create a new project on the server",
        status_codes={
            201: "Project created",
            403: "Forbidden to create a project",
            409: "Project already created"
        },
        output=PROJECT_OBJECT_SCHEMA,
        input=PROJECT_CREATE_SCHEMA)
    def create_project(request, response):

        pm = ProjectManager.instance()
        p = pm.create_project(
            name=request.json.get("name"),
            path=request.json.get("path"),
            project_id=request.json.get("project_id")
        )
        response.set_status(201)
        response.json(p)

    @Route.get(
        r"/projects/{project_id}",
        description="Get project information",
        parameters={
            "project_id": "Project UUID",
        },
        status_codes={
            200: "Success",
            404: "The project doesn't exist"
        },
        output=PROJECT_OBJECT_SCHEMA)
    def show(request, response):

        pm = ProjectManager.instance()
        project = pm.get_project(request.match_info["project_id"])
        response.json(project)

    @Route.post(
        r"/projects/{project_id}/close",
        description="Close a project",
        parameters={
            "project_id": "Project UUID",
        },
        status_codes={
            204: "Project closed",
            404: "The project doesn't exist"
        })
    def close(request, response):

        pm = ProjectManager.instance()
        project = pm.get_project(request.match_info["project_id"])
        if ProjectHandler._notifications_listening.setdefault(project.id, 0) <= 1:
            yield from project.close()
            pm.remove_project(project.id)
            try:
                del ProjectHandler._notifications_listening[project.id]
            except KeyError:
                pass
        else:
            log.warning("Skip project closing, another client is listening for project notifications")
        response.set_status(204)

    @Route.delete(
        r"/projects/{project_id}",
        description="Delete a project from disk",
        parameters={
            "project_id": "Project UUID",
        },
        status_codes={
            204: "Changes have been written on disk",
            404: "The project doesn't exist"
        })
    def delete(request, response):

        pm = ProjectManager.instance()
        project = pm.get_project(request.match_info["project_id"])
        yield from project.delete()
        pm.remove_project(project.id)
        response.set_status(204)

    @Route.get(
        r"/projects/{project_id}/notifications",
        description="Receive notifications about the project",
        parameters={
            "project_id": "Project UUID",
        },
        status_codes={
            200: "End of stream",
            404: "The project doesn't exist"
        })
    def notification(request, response):

        pm = ProjectManager.instance()
        project = pm.get_project(request.match_info["project_id"])

        response.content_type = "application/json"
        response.set_status(200)
        response.enable_chunked_encoding()

        response.start(request)
        queue = project.get_listen_queue()
        ProjectHandler._notifications_listening.setdefault(project.id, 0)
        ProjectHandler._notifications_listening[project.id] += 1
        response.write("{}\n".format(json.dumps(ProjectHandler._getPingMessage())).encode("utf-8"))
        while True:
            try:
                (action, msg) = yield from asyncio.wait_for(queue.get(), 5)
                if hasattr(msg, "__json__"):
                    msg = json.dumps({"action": action, "event": msg.__json__()}, sort_keys=True)
                else:
                    msg = json.dumps({"action": action, "event": msg}, sort_keys=True)
                log.debug("Send notification: %s", msg)
                response.write(("{}\n".format(msg)).encode("utf-8"))
            except asyncio.futures.CancelledError as e:
                break
            except asyncio.futures.TimeoutError:
                response.write("{}\n".format(json.dumps(ProjectHandler._getPingMessage())).encode("utf-8"))
        project.stop_listen_queue(queue)
        if project.id in ProjectHandler._notifications_listening:
            ProjectHandler._notifications_listening[project.id] -= 1

    def _getPingMessage(cls):
        """
        Ping messages are regularly sent to the client to
        keep the connection open. We send with it some information about server load.

        :returns: hash
        """
        stats = {}
        # Non blocking call in order to get cpu usage. First call will return 0
        stats["cpu_usage_percent"] = psutil.cpu_percent(interval=None)
        stats["memory_usage_percent"] = psutil.virtual_memory().percent
        return {"action": "ping", "event": stats}

    @Route.get(
        r"/projects/{project_id}/files",
        description="List files of a project",
        parameters={
            "project_id": "Project UUID",
        },
        status_codes={
            200: "Return a list of files",
            404: "The project doesn't exist"
        },
        output=PROJECT_FILE_LIST_SCHEMA)
    def list_files(request, response):

        pm = ProjectManager.instance()
        project = pm.get_project(request.match_info["project_id"])
        files = yield from project.list_files()
        response.json(files)
        response.set_status(200)

    @Route.get(
        r"/projects/{project_id}/files/{path:.+}",
        description="Get a file from a project",
        parameters={
            "project_id": "Project UUID",
        },
        status_codes={
            200: "File returned",
            403: "Permission denied",
            404: "The file doesn't exist"
        })
    def get_file(request, response):

        pm = ProjectManager.instance()
        project = pm.get_project(request.match_info["project_id"])
        path = request.match_info["path"]
        path = os.path.normpath(path)

        # Raise error if user try to escape
        if path[0] == ".":
            raise aiohttp.web.HTTPForbidden
        path = os.path.join(project.path, path)

        response.content_type = "application/octet-stream"
        response.set_status(200)
        response.enable_chunked_encoding()

        try:
            with open(path, "rb") as f:
                yield from response.prepare(request)
                while True:
                    data = f.read(4096)
                    if not data:
                        break
                    yield from response.write(data)

        except FileNotFoundError:
            raise aiohttp.web.HTTPNotFound()
        except PermissionError:
            raise aiohttp.web.HTTPForbidden()

    @Route.get(
        r"/projects/{project_id}/stream/{path:.+}",
        description="Stream a file from a project",
        parameters={
            "project_id": "Project UUID",
        },
        status_codes={
            200: "File returned",
            403: "Permission denied",
            404: "The file doesn't exist"
        })
    def stream_file(request, response):

        pm = ProjectManager.instance()
        project = pm.get_project(request.match_info["project_id"])
        path = request.match_info["path"]
        path = os.path.normpath(path)

        # Raise an error if user try to escape
        if path[0] == ".":
            raise aiohttp.web.HTTPForbidden
        path = os.path.join(project.path, path)

        response.content_type = "application/octet-stream"
        response.set_status(200)
        response.enable_chunked_encoding()

        try:
            with open(path, "rb") as f:
                yield from response.prepare(request)
                while True:
                    data = f.read(4096)
                    if not data:
                        yield from asyncio.sleep(0.1)
                    yield from response.write(data)

        except FileNotFoundError:
            raise aiohttp.web.HTTPNotFound()
        except PermissionError:
            raise aiohttp.web.HTTPForbidden()

    @Route.post(
        r"/projects/{project_id}/files/{path:.+}",
        description="Write a file to a project",
        parameters={
            "project_id": "Project UUID",
        },
        raw=True,
        status_codes={
            200: "File returned",
            403: "Permission denied",
            404: "The path doesn't exist"
        })
    def write_file(request, response):

        pm = ProjectManager.instance()
        project = pm.get_project(request.match_info["project_id"])
        path = request.match_info["path"]
        path = os.path.normpath(path)

        # Raise error if user try to escape
        if path[0] == ".":
            raise aiohttp.web.HTTPForbidden
        path = os.path.join(project.path, path)

        response.set_status(200)

        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'wb+') as f:
                while True:
                    packet = yield from request.content.read(512)
                    if not packet:
                        break
                    f.write(packet)

        except FileNotFoundError:
            raise aiohttp.web.HTTPNotFound()
        except PermissionError:
            raise aiohttp.web.HTTPForbidden()

    @Route.get(
        r"/projects/{project_id}/export",
        description="Export a project as a portable archive",
        parameters={
            "project_id": "Project UUID",
        },
        raw=True,
        status_codes={
            200: "File returned",
            404: "The project doesn't exist"
        })
    def export_project(request, response):

        pm = ProjectManager.instance()
        project = pm.get_project(request.match_info["project_id"])
        response.content_type = 'application/gns3project'
        response.headers['CONTENT-DISPOSITION'] = 'attachment; filename="{}.gns3project"'.format(project.name)
        response.enable_chunked_encoding()
        yield from response.prepare(request)

        include_images = bool(int(request.json.get("include_images", "0")))
        for data in project.export(include_images=include_images):
            response.write(data)
            yield from response.drain()

        yield from response.write_eof()

    @Route.post(
        r"/projects/{project_id}/import",
        description="Import a project from a portable archive",
        parameters={
            "project_id": "Project UUID",
        },
        raw=True,
        output=PROJECT_OBJECT_SCHEMA,
        status_codes={
            200: "Project imported",
            403: "Forbidden to import project"
        })
    def import_project(request, response):

        pm = ProjectManager.instance()
        project_id = request.match_info["project_id"]
        project = pm.create_project(project_id=project_id)

        # We write the content to a temporary location and after we extract it all.
        # It could be more optimal to stream this but it is not implemented in Python.
        # Spooled means the file is temporary kept in memory until max_size is reached
        try:
            with tempfile.SpooledTemporaryFile(max_size=10000) as temp:
                while True:
                    packet = yield from request.content.read(512)
                    if not packet:
                        break
                    temp.write(packet)
                project.import_zip(temp, gns3vm=bool(int(request.GET.get("gns3vm", "1"))))
        except OSError as e:
            raise aiohttp.web.HTTPInternalServerError(text="Could not import the project: {}".format(e))

        response.json(project)
        response.set_status(201)
