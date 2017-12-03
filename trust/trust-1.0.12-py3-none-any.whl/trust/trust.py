import trust
import trust.formatters


class Trust():
    def __init__(self, finder):
        self._finder = finder

    def process(self, query, response_mode, credentials, optional=False):
        formatter = self._map_formatter(response_mode)
        if not self._is_query_valid(query):
            return formatter.reject_invalid()

        return formatter.process(query, credentials, optional)

    def _is_query_valid(self, query):
        if "/../" in query or query.endswith("/.."):
            return False

        if query.startswith("/_users/") or query == "/_users":
            return False

        if query.startswith("/_groups/") or query == "/_groups":
            return False

        return True

    def _map_formatter(self, response_mode):
        formatter_type = {
            "json": trust.formatters.JsonFormatter,
            "text": trust.formatters.TextFormatter,
            "complete": trust.formatters.CompleteFormatter,
        }.get(response_mode or "complete", None)

        if formatter_type is None:
            raise trust.FormatterException(
                ("The formatter corresponding to response mode %s doesn't " +
                 "exist.") % (response_mode,)
            )

        return formatter_type(self._finder)


class Credentials():
    def __init__(self, username, password):
        self._username = username
        self._password = password

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @property
    def are_empty(self):
        return self._username is None

    @staticmethod
    def get_empty():
        return Credentials(None, None)
