import re
from functools import wraps

def ensure_bytes(x):
    if x == None:
        raise StopIteration
    elif isinstance(x, bytes):
        yield x
        raise StopIteration
    elif hasattr(x, '__iter__') and not isinstance(x, str):
        for y in x:
            if isinstance(y, bytes):
                yield y
            else:
                break
        else:
            raise StopIteration
    raise TypeError('Functions in this interface must return bytes or iterables of bytes.')

def _url_template(section, s):
    signature = ''
    for x in section:
        signature += '/%s' % x
    for x in s.positional:
        signature += '/:%s' % x.name
    for x in s.keyword1:
        signature += '/[%s]' % x.name
    for x in s.var_positional:
        signature += '/&lt;%s&gt;' % x.name
    signature += '?(option=...)'
    return signature

def _as_bytes(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        text = '\n'.join(function(*args, **kwargs))
        return ('<main>%s</main>' % text).encode('utf-8')
    return wrapper

def _endpoints(prog, section):
    for subsection in prog.subset(section):
        function = prog[subsection]
        yield (
            '/' + '/'.join(subsection),
            _url_template(subsection, function),
        )

@_as_bytes
def usage(prog, h):
    endpoints = _endpoints(prog, h.section)

    if h.message:
        yield '<em>%s</em>' % h.message
    yield '<ul>'
    for endpoint in endpoints:
        yield '<li><a href="%s"><code>%s</code></a></li>' % endpoint
    yield '</ul>'

@_as_bytes
def man(prog, h):
    function = prog[h.section] # XXX
    endpoints = _endpoints(prog, h.section)
    description = list(filter(None, re.split('r[\n\r]{2,}', function.description)))
    args = function.all_positionals()
    kwargs = function.keyword2

    yield '''\
<h2>Synopsis<h2>
<ul>
'''
    for i, signature in enumerate(endpoints):
        yield '<li><a href="%s"><code>%s</code></a></li>' % signature
    yield '</ul>'
    if description:
        yield '<h2>Description</h2>'
        for p in description:
            yield '<p>%s</p>' % p

    if args:
        yield '''\
<h3>Inputs</h3>
<dl>
'''
        for arg in args:
            yield '<dt>%s</dt><dd>%s</dt>\n' % (arg.name, arg.description)
        yield '</dl>\n'

    if kwargs:
        yield '''\
<h3>Options</h3>
<dl>
'''
        for pair in kwargs:
            yield '<dt>%s</dt><dd>%s</dd>' % pair
        yield '</dl>'

    yield '''\
<h2>Detail</h2>
<p>
  Put "help" in the query string ("?help") for more help.
</p>
'''
