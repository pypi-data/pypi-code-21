import os
import json

from findex_common.exceptions import JsonParseException
from findex_common.static_variables import DefaultPorts


class CrawlController:
    @staticmethod
    def make_valid_key(filename):
        if filename == "*":
            return "*"

        rtn = filename.lower()

        for remove in ['-', ',', '+', '_']:
            rtn = rtn.replace(remove, ' ')

        if '.' in rtn:
            rtn = os.path.splitext(rtn)
            rtn = rtn[0].replace('.', ' ')

        if len(rtn) > 40:
            rtn = rtn[:40]
            rtn = rtn.strip()
        elif len(rtn) < 2:
            return
        return rtn

    @staticmethod
    def crawl_message_make(resource):
        """
        Resource -> JSON task
        :param resource: `findex_gui.orm.models.resource`
        :return: JSON blob
        """
        try:
            return {
                'address': resource.server.address,
                'port': resource.port,
                'method': resource.protocol_human,
                'basepath': resource.basepath,
                'name': resource.server.name,
                'options': {
                    'display_url': resource.display_url,
                    'user-agent': resource.meta.user_agent,
                    'auth_user': resource.meta.auth_user,
                    'auth_pass': resource.meta.auth_pass,
                    'depth': resource.meta.depth,
                    'file_distribution': resource.meta.file_distribution,
                    'recursive_foldersizes': resource.meta.recursive_sizes,
                    'throttle_connections': resource.meta.throttle_connections
                }
            }
        except ValueError:
            return
        except Exception as ex:
            return

    @staticmethod
    def crawl_message_parse(data):
        if not isinstance(data, dict):
            if isinstance(data.data, bytes):
                data.data = data.data.decode("latin")
            data = json.loads(data.data)

        for c in ["method", "address", "basepath", "options"]:
            if c not in data:
                raise JsonParseException("crawl_message parse error: missing key '%s'" % c)

        if not isinstance(data["options"], dict):
            raise JsonParseException("crawl_message parse error: missing key 'options'; should be a dict")

        if data["basepath"].endswith("/"):
            data["basepath"] = data["basepath"][:-1]
        elif not data["basepath"].startswith("/") and len(data["basepath"]) > 1:
            data["basepath"] = "/%s" % data["basepath"]

        if "display_url" not in data["options"]:
            data["display_url"] = "%s://%s%s" % (
                data["resource_protocol"], 
                data["server_address"], 
                data["basepath"])

        if "port" not in data:
            data["resource_port"] = DefaultPorts().id_by_name(data["resource_protocol"])
        else:
            try:
                port = int(data["port"])
                if not 0 <= port <= 65536:
                    raise Exception
            except:
                raise JsonParseException("port needs to be a number between 1 and 65535")

        options = data["options"]

        if "auth_user" not in options:
            data["auth_user"] = None

        if "auth_pass" not in options:
            data["auth_pass"] = None

        if "depth" in options and isinstance(options["depth"], str):
            try:
                options["depth"] = int(options["depth"])
            except:
                raise JsonParseException("depth should be an integer")

        return data