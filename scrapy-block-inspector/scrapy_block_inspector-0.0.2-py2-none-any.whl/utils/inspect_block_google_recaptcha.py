import re

pattern_recaptcha = re.compile(
    r'(?P<recaptcha_api>www\.google\.com\/recaptcha\/api\.js)',
    flags=re.VERBOSE)


def _inspect_block(response):
    for _ in map(lambda x: pattern_recaptcha.search(x),
                 response.css('script::attr(src)').extract()):
        yield _


def inspect_block(response):
    return any(_inspect_block(response))
