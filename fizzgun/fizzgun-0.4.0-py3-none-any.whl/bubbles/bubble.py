from typing import Iterable, Dict

from fizzgun.application.dependencies import IdGenerator, RandomGenerator
from fizzgun.models import Expectations, HttpRequest


class Bubble(object):
    """
    Main abstract class for every bubble. Subclasses must implement (at least) the generate method
    """
    def __init__(self, id_generator: IdGenerator, random_generator: RandomGenerator, *args, **kwargs):
        self._id_generator = id_generator
        self._random_generator = random_generator
        self._expectations = Expectations()
        self._mark_requests = False
        self.initialize(*args, **kwargs)

    def initialize(self, expected_status_range='0-499', mark_requests=False, *_args, **_kwargs):
        """
        Subclasses can re-implement this method to configure themselves.
        Usually they should invoke super so the global configuration is set up
        """
        self.expectations.expect('status').to.be_in_ranges(expected_status_range)
        self._mark_requests = mark_requests

    @property
    def expectations(self) -> Expectations:
        return self._expectations

    @property
    def description(self) -> str:
        doc = self.__class__.__doc__
        if doc:
            return str(doc.strip())
        return 'undefined'

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def generate(self, request: HttpRequest) -> Iterable[Dict]:
        raise NotImplementedError("Method 'generate' must be implemented in %s" % self.name)

    def inflate(self, request: HttpRequest) -> Iterable[Dict]:
        if self.does_apply(request):
            if self._mark_requests:
                return self._generate_with_mark(request)
            else:
                return self.generate(request)
        return []

    def does_apply(self, _request) -> bool:
        return True

    def _generate_with_mark(self, request) -> Iterable[Dict]:
        for mutant in self.generate(request):
            mutant['headers'].append(('x-fizzgun-id', self._id_generator.generate()))
            yield mutant
