import trust
import trust.audit
import json
import logging
import os
from .auth import InDataAuthProvider
from .exceptions import AuthenticationException, NodeNotFoundException, \
        CircularInheritanceException
from .zipper import Zipper


class FileFinder():
    def __init__(self, data_path, logger=None, audit=None):
        self._data_path = data_path
        self._logger = logger or logging.getLogger(__name__)
        self._audit = audit or trust.audit.NullAudit()
        self._is_authenticated = False
        self._credentials = None
        self._auth_provider = None

    @property
    def username(self):
        return (None
                if self._credentials is None
                else self._credentials.username)

    @property
    def auth_provider(self):
        return self._auth_provider or InDataAuthProvider(self, self._logger)

    @auth_provider.setter
    def auth_provider(self, value):
        self._auth_provider = value

    def find(self, path, optional=False, previous_inheritance_paths=[]):
        if len(path) == 0:
            raise ValueError("The path shouldn't be empty.")

        if path[0] != "/":
            raise ValueError(
                "The path should start with a slash. The character '%s' is "
                "unexpected." % (path[0],))

        self._logger.info("The loader is finding %s.", path)

        result = self._find(path, optional, previous_inheritance_paths)

        if path == "/":
            del result["_users"]
            del result["_groups"]

        return result

    def _find(self, path, optional=False, previous_inheritance_paths=[]):
        parts = self._split_path(path)
        json, remaining_parts = self._find_json(parts)
        parts_taken = parts[:len(parts) - len(remaining_parts)]

        if json is None:
            if parts_taken[-1] == ".keys":
                names = sorted(self._list_files_in_directory(parts_taken))
                return list(names)

            directory = self._explore_directory(parts_taken + remaining_parts)
            if not optional and directory is None:
                raise NodeNotFoundException

            return directory

        return self._extract(
            parts_taken, remaining_parts, json, optional,
            previous_inheritance_paths=previous_inheritance_paths
        )

    def access_as(self, credentials):
        self._is_authenticated = False
        self._credentials = credentials

    def _authenticate(self):
        if self.username is None:
            self._logger.debug("No user to authenticate.")
            return

        self._logger.debug(
            "Authenticating user %s.", self.username
        )

        auth_result = self.auth_provider.verify(self._credentials)
        self._logger.info("Audit: %s." % (self._audit,))
        self._logger.info("Authentication result: %s." % (auth_result,))
        self._audit.user_verified(self.username, auth_result)

        if not auth_result:
            self._logger.info("User %s failed to authenticate.", self.username)
            raise AuthenticationException

        self._logger.info("User %s logged on.", self.username)

    def _extract(self, path, parts, obj, optional, skip_restricted=False,
                 previous_inheritance_paths=[]):
        self._logger.debug("Processing %s: %s.", path, parts)

        keys = obj.keys() if type(obj) is dict else []

        if ".special:restricted" in keys:
            if not self._verify_access(obj[".special:restricted"]):
                if skip_restricted:
                    return None

                self._audit.restricted_node_accessed(
                    self.username, "/".join(path), False
                )
                raise PermissionError()

            self._audit.restricted_node_accessed(
                self.username, "/".join(path), True
            )

            del obj[".special:restricted"]

            if ".special:value" in keys:
                return self._extract(
                    path, parts, obj[".special:value"], optional,
                    previous_inheritance_paths=previous_inheritance_paths
                )

        if ".special:inherit" in keys:
            obj = self._inherit(obj, previous_inheritance_paths)

        if len(parts) == 0:
            if type(obj) is list:
                self._logger.debug("The object is an array.")
                result = []
                for current in obj:
                    array_item = self._extract(
                        path, [], current, optional,
                        previous_inheritance_paths=previous_inheritance_paths
                    )

                    result.append(array_item)

                return result

            if type(obj) is not dict:
                self._logger.debug("The object is a scalar.")
                return obj

            result = {}
            for c in obj:
                result[c] = self._extract(
                    path, [], obj[c], optional, skip_restricted=True,
                    previous_inheritance_paths=previous_inheritance_paths
                )

            return result

        name = parts[0]

        special = self._process_special_keys(name, obj)
        if special is not None:
            return special

        if name.startswith(".plain:"):
            name = name[7:]

        try:
            current = obj[name]
        except TypeError:
            current = obj[int(name)]
        except KeyError:
            if optional:
                return None

            # Breaking the stack is intentional here.
            raise NodeNotFoundException

        if len(parts) == 1:
            if type(current) is not dict and type(current) is not list:
                return current

            return self._extract(
                path + parts, [], current, optional,
                previous_inheritance_paths=previous_inheritance_paths
            )

        return self._extract(
            path + [name], parts[1:], current, optional,
            previous_inheritance_paths=previous_inheritance_paths
        )

    def _verify_access(self, restrictions):
        if not self._is_authenticated:
            self._authenticate()

        if self.username is None:
            self._logger.debug("A guest is trying to access restricted data.")
            return False

        users = restrictions.get("users", [])
        self._logger.debug("The following users can access data: %s.", users)
        if self.username in users:
            return True

        groups = restrictions.get("groups", [])
        self._logger.debug("The following groups can access data: %s.", groups)
        for group in groups:
            if self.auth_provider.ingroup(self.username, group):
                return True

        return False

    def _explore_directory(self, parts):
        """
        Generates the JSON representation of the directory and JSON files
        within the directory and the subdirectories.

        Returns either an object corresponding to the JSON representation of
        the data, or None if the directory doesn't exist.
        """
        dir_path = os.path.join(self._data_path, "/".join(parts))
        self._logger.debug("Exploring the directory %s (%s).", parts, dir_path)
        base_path = "".join(["/" + c for c in parts])
        response = {}

        if not os.path.isdir(dir_path):
            return None

        for name in os.listdir(dir_path):
            path = os.path.join(dir_path, name)
            if path.endswith(".json") and os.path.isfile(path):
                short_name = name[:-5]
                query_path = "/".join([base_path, short_name])
                response[short_name] = self.find(query_path)

            if os.path.isdir(path):
                response[name] = self._explore_directory(parts + [name])

        return response

    def _list_files_in_directory(self, parts):
        dir_path = os.path.join(self._data_path, "/".join(parts[:-1]))
        self._logger.debug("Listing contents of directory %s.", dir_path)
        for name in os.listdir(dir_path):
            path = os.path.join(dir_path, name)
            if path.endswith(".json") and os.path.isfile(path):
                short_name = name[:-5]
                yield short_name

    def _process_special_keys(self, name, obj):
        if name == '.keys':
            keys = obj.keys()
            return sorted(obj.keys())

        return None

    def _inherit(self, obj, previous_inheritance_paths):
        parent_path = obj[".special:inherit"]
        if parent_path in previous_inheritance_paths:
            raise CircularInheritanceException()

        self._logger.debug("Inheriting on %s.", parent_path)
        parent = self.find(
            parent_path, False, previous_inheritance_paths + [parent_path]
        )

        self._logger.debug("Got %s through inheritance. Combining.", parent)
        del obj[".special:inherit"]
        return Zipper(obj, parent, self._logger).zip()

    def _split_path(self, path):
        normalized_path = path.lstrip("/")
        return normalized_path.split("/")

    def _find_json(self, parts):
        """
        Finds the first JSON file which matches the parts.

        Returns a tuple containing:

         - The JSON corresponding to the first JSON file matching the criteria,
           or None if there are no matches.
         - The parts which were not used for the path to the JSON file.
        """
        remaining_parts = parts
        for file_path in self._list_json_file_candidates(parts):
            remaining_parts = remaining_parts[1:]
            full_path = os.path.join(self._data_path, file_path)
            self._logger.debug("Checking for %s.", full_path)
            if os.path.isfile(full_path):
                with open(full_path) as f:
                    return (json.load(f), remaining_parts)

        return (None, remaining_parts)

    def _list_json_file_candidates(self, parts):
        """
        Lists the JSON file candidates which may be used based on the current
        parts list. For instance, the parts ["a", "b", "c"] will yield three
        paths:
         - a.json
         - a/b.json
         - a/b/c.json
        """
        for path in self._aggregate_parts_in_path(parts):
            yield path[:-1] + ".json"

    def _aggregate_parts_in_path(self, parts):
        """
        Aggregates the path parts to progressively form longer and longer
        paths. For instance, the parts ["a", "b", "c"] will yield three paths:
         - a/
         - a/b/
         - a/b/c/
        The paths contain trailing slash but no leading slash.
        """
        path = ""
        for part in parts:
            path = path + part + "/"
            yield path
