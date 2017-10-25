import collections
import hashlib
import re

from fizzgun.application.service_contexts import FilterContext
from fizzgun.core.common import Worker
from fizzgun.models import HttpRequest


class Filter(Worker):

    def initialize(self, filters_config=None):
        self._request_filter = RequestFilter(filters_config or [])
        self._stdout_writer = self.filter_context.stdout_writer

    def process(self, work):
        request = HttpRequest(work['original'])

        if self._request_filter.accept(request):
            self._stdout_writer.write("Processing request for host '%s'" % request.endpoint)
            yield work
        else:
            self._stdout_writer.write("Request to host '%s' filtered" % request.endpoint)

    @property
    def filter_context(self) -> FilterContext:
        return self.service_context


class RequestFilter(object):
    def __init__(self, rule_set):
        self._rule_set = rule_set

        self._matcher_set = {
            'path': lambda pattern, request: self._pattern_matches(pattern, request.path),
            'path_with_query': lambda pattern, request: self._pattern_matches(pattern, request.path_with_query),
            'method': lambda methods, request: (isinstance(methods, str) and
                                                request.method == methods.upper()) or any(
                m.upper() == request.method for m in methods),
            'unseen': self._matcher_request_unseen,
            'unknown': lambda _args, _request: True
        }

        self._seen_signatures = collections.deque([], maxlen=1000)

    def accept(self, request: HttpRequest) -> bool:
        if not self._rule_set:
            return True
        rules = self._endpoint_rules(request.endpoint)
        return self._is_whitelisted(rules, request)

    def _endpoint_rules(self, endpoint):
        return [rule for rule in self._rule_set if self._pattern_matches(rule['endpoint'], endpoint)]

    def _is_whitelisted(self, rules, request):
        for rule in rules:
            matchers = rule.get('matchers')

            if not matchers:
                return True

            if self._matches(matchers, request):
                return True

        return False

    def _matches(self, match_group, request):
        return all(self._matcher_set.get(match_type, self._matcher_set['unknown'])(arguments, request)
                   for match_type, arguments in match_group.items())

    def _pattern_matches(self, pattern, string):
        if pattern == '*' or pattern == string:
            return True
        try:
            regex = re.compile("^%s$" % pattern)
            if regex.search(string):
                return True
        except re.error:
            pass
        return False

    def _matcher_request_unseen(self, keys, request):
        payload = ""
        for k in sorted(keys):
            payload += str(getattr(request, k, ''))
        signature = hashlib.md5(payload.encode('utf-8')).digest()

        ret = signature not in self._seen_signatures
        self._seen_signatures.append(signature)
        return ret
