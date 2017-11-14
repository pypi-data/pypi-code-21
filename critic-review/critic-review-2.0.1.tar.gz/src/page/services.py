# -*- mode: python; encoding: utf-8 -*-
#
# Copyright 2012 Jens Lindström, Opera Software ASA
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License.  You may obtain a copy of
# the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations under
# the License.

import os
import time

import background
import dbutils
import htmlutils
import page.utils

def renderServices(req, db, user):
    req.content_type = "text/html; charset=utf-8"

    document = htmlutils.Document(req)
    document.setTitle("Services")

    html = document.html()
    head = html.head()
    body = html.body()

    page.utils.generateHeader(body, db, user, current_page="services")

    document.addExternalStylesheet("resource/services.css")
    document.addExternalScript("resource/services.js")
    document.addInternalScript(user.getJS())

    try:
        response = background.utils.issue_command(
            "servicemanager", {"query": "status"},
            timeout=10)
    except (ConnectionRefusedError, background.utils.TimeoutError):
        raise page.utils.DisplayMessage("Service manager not responding!")

    if response["status"] == "error":
        raise page.utils.DisplayMessage(response["error"])

    paleyellow = page.utils.PaleYellowTable(body, "Services")

    def render(target):
        table = target.table("services callout")

        headings = table.tr("headings")
        headings.th("name").text("Name")
        headings.th("module").text("Module")
        headings.th("pid").text("PID")
        headings.th("rss").text("RSS")
        headings.th("cpu").text("CPU")
        headings.th("uptime").text("Uptime")
        headings.th("commands").text()

        table.tr("spacer").td("spacer", colspan=4)

        def formatUptime(seconds):
            def inner(seconds):
                if seconds < 60: return "%d seconds" % seconds
                elif seconds < 60 * 60: return "%d minutes" % (seconds / 60)
                elif seconds < 60 * 60 * 24: return "%d hours" % (seconds / (60 * 60))
                else: return "%d days" % (seconds / (60 * 60 * 24))
            if seconds is None:
                return ""
            return inner(int(seconds)).replace(" ", "&nbsp;")

        def formatRSS(bytes):
            if bytes < 1024: return "%d B" % bytes
            elif bytes < 1024 ** 2: return "%.1f kB" % (float(bytes) / 1024)
            elif bytes < 1024 ** 3: return "%.1f MB" % (float(bytes) / 1024 ** 2)
            else: return "%.1f GB" % (float(bytes) / 1024 ** 3)

        def formatCPU(seconds):
            minutes = int(seconds / 60)
            seconds = seconds - minutes * 60
            seconds = "%2.2f" % seconds
            if seconds.find(".") == 1: seconds = "0" + seconds
            return "%d:%s" % (minutes, seconds)

        def getProcessData(pid):
            try:
                items = open("/proc/%d/stat" % pid).read().split()

                return { "cpu": formatCPU(float(int(items[13]) + int(items[14])) / os.sysconf("SC_CLK_TCK")),
                         "rss": formatRSS(int(items[23]) * os.sysconf("SC_PAGE_SIZE")) }
            except:
                return { "cpu": "N/A",
                         "rss": "N/A" }

        for service_name, service_data in sorted(response["services"].items()):
            process_data = getProcessData(service_data["pid"])

            row = table.tr("service")
            row.td("name").text(service_name)
            row.td("module").text(service_data["module"])
            row.td("pid").text(service_data["pid"] if service_data["pid"] else "(not running)")
            row.td("rss").text(process_data["rss"])
            row.td("cpu").text(process_data["cpu"])
            row.td("uptime").innerHTML(formatUptime(service_data["uptime"]))

            commands = row.td("commands")
            commands.a(href="javascript:void(restartService(%s));" % htmlutils.jsify(service_name)).text("[restart]")
            commands.a(href="javascript:void(getServiceLog(%s));" % htmlutils.jsify(service_name)).text("[log]")

    paleyellow.addCentered(render)

    return document
