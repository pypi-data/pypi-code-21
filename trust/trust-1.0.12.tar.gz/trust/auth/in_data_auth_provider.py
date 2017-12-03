import time
from passlib.hash import pbkdf2_sha256


class InDataAuthProvider():
    def __init__(self, finder, logger):
        self._finder = finder
        self._logger = logger
        self._logger.debug("In-data authentication provider initialized.")

    def verify(self, credentials):
        self._logger.debug("Authentication provider is verifying a user.")
        password_hash = self._finder.find(
            "/_users/" + credentials.username + "/hash"
        )

        start_time = time.time()
        result = pbkdf2_sha256.verify(credentials.password, password_hash)
        end_time = time.time()
        self._logger.debug(
            "PBKDF2 verification done in %s ms. resulting in %s.",
            int(end_time - start_time),
            result)

        return result

    def ingroup(self, username, groupname):
        return groupname in self._get_groups(
            "/_users/" + username + "/member-of"
        )

    def _get_groups(self, path):
        """
        Retrieves the groups the user or group belongs to.
        """
        groups = list(set(self._finder.find(path, optional=True) or []))

        i = 0
        while i < len(groups):
            current = groups[i]
            i = i + 1
            yield current

            child_path = "/_groups/" + current + "/member-of"
            children = self._finder.find(child_path, optional=True) or []
            self._add_unique(groups, children)

    @staticmethod
    def _add_unique(current_list, values):
        """
        Extends a list by adding the values which are not yet in the list.
        """
        current_list.extend([c for c in values if c not in current_list])
