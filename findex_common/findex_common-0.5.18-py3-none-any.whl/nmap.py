import os
import random
from datetime import datetime

from findex_common.static_variables import FileProtocols


class NmapScan:
    def __init__(self, twisted=False):
        """
        :param twisted: Set the True if called from `findex-crawl` (enables txpostgres queries
        instead of SQLa)
        """
        self.twisted = twisted

    def scan(self, cmd):
        """unsafe method, should only be called by the admin. Yolo nmap parsing"""
        # @TODO: convert to twisted non-blocking
        if "-oG -" not in cmd:
            raise Exception("\"-oG -\" is required in nmap cmd")
        if os.popen("whereis nmap").read().count(" ") <= 1:
            raise Exception("nmap not found in $PATH, nmap not installed?")

        hosts = []
        results = os.popen("%s | grep open" % cmd).read()
        results = str(results)
        for line in [line.rstrip().lower() for line in results.split("\n") if line]:
            if not line.startswith("host: ") or "ports:" not in line:
                continue
            try:
                host = line[6:].split(" ", 1)[0]
                line = line[line.find("\t") + 8:]

                items = line.split("/, ")
                for item in items:
                    port, status, ip_protocol, not_sure, service, not_sure2, banner = item.split("/", 6)
                    if status != "open":
                        continue

                    port = int(port)
                    hosts.append({
                        "host": host,
                        "port": port,
                        "service": service})
            except Exception as ex:
                pass

        return hosts

    def nmap_to_resource(self, task, scan_results):
        """
        :param scan_results:
        :return: returns added resources
        """
        if not scan_results:
            raise Exception("no nmap tasks")

        added_resources = []
        for scan_result in scan_results:
            resource = None
            try:
                resource = self.get_resources(address=scan_result["host"],
                                              port=scan_result["port"])
            except:
                pass

            if not resource:
                if scan_result["service"] not in FileProtocols().get_names():
                    self.log_msg("Discovered service \"%s://%s:%d\" not recognized - should be any of: (%s)" % (
                        scan_result["service"],
                        scan_result["host"],
                        scan_result["port"],
                        ", ".join(FileProtocols().get_names())), level=1)
                    continue
                else:
                    name = "%s_%s" % (task.name, random.randrange(10 ** 8))
                    try:
                        resource = self.add_resource(name,
                                                     server_address=scan_result["host"],
                                                     resource_port=scan_result["port"],
                                                     resource_protocol=FileProtocols().id_by_name(scan_result["service"]),
                                                     server_name=name,
                                                     description="Discovered via nmap",
                                                     display_url="/",
                                                     recursive_sizes=True,
                                                     throttle_connections=-1,
                                                     current_user=0)
                        added_resources.append(resource)
                    except Exception as ex:
                        self.log_msg("Could not auto-add resource (%s:%d) with name \"%s\": %s" % (
                            name, scan_result["host"], scan_result["port"], str(ex)
                        ), level=2)
                        continue

                    self.log_msg("Discovered service \"%s://%s:%d\" - auto-adding as \"%s\"" % (
                        scan_result["service"],
                        scan_result["host"],
                        scan_result["port"],
                        name))

        return added_resources

    def update_nmap_task(self, nmap_task, **kwargs):
        for k, v in kwargs.items():
            setattr(nmap_task, k, v)

        if self.twisted:
            pass
        else:
            from findex_gui.web import db
            db.session.commit()
            db.session.flush()

    def get_resources(self, **kwargs):
        if self.twisted:
            pass
        else:
            from findex_gui.controllers.resources.resources import ResourceController
            return ResourceController.get_resources(**kwargs)

    def add_resource(self, name, **kwargs):
        if self.twisted:
            pass
        else:
            from findex_gui.controllers.resources.resources import ResourceController
            return ResourceController.add_resource(**kwargs)

    def log_msg(self, *args, **kwargs):
        """
        Logs a message
        :param msg: msg
        :param level: 0: DEBUG, 1: INFO, 2: WARNING, 3: ERROR
        :return:
        """
        if self.twisted:
            pass
        else:
            from findex_gui.bin.utils import log_msg as _log_msg
            _log_msg(*args, **kwargs)
