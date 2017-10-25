from fizzgun.core.common import Worker
from fizzgun.models import Expectations


class Assertor(Worker):
    """
    Perform assertions on HTTP responses of mutated requests, and forwards the result
    to the next node in the chain if any assertion fails.
    """
    def process(self, work):
        response = work['response']
        expectations = work['expectations']
        success, errors = self.check(response, expectations)
        if not success:
            work['errors'] = errors
            yield work

    def check(self, response, expectations):
        expect = Expectations._unmarshall(expectations)
        return expect._verify(response)
