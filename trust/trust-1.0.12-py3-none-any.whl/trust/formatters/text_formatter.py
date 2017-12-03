import trust
import json


class TextFormatter():
    def __init__(self, finder):
        self._finder = finder

    def process(self, query, credentials, optional=False):
        self._finder.access_as(credentials)
        result = self._finder.find(query, optional=optional)

        if result is None:
            return ""
        if type(result) is list:
            return "\n".join(
                [self._process_list_element(c) for c in result]
            )
        elif type(result) is str:
            return result

        return json.dumps(result, sort_keys=True)

    def reject_invalid(self):
        raise trust.InvalidQueryException

    def _process_list_element(self, element):
        return (
            str(
                json.dumps(element, sort_keys=True)
                if type(element) is dict
                else element
            )
        )
