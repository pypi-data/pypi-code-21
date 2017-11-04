# -*- coding: utf-8 -*-

from dktasklib.wintask import task
import base64
import os
import re
import urllib


def inline_data(data, type='image/png', name=""):
    """Inline (encode) the ``data``.
    """
    if len(data) > 10 * 1024:
        print "%s is too big (%d bytes), max is 10KB" % (name, len(data))
        return name

    encoded = base64.b64encode(data)
    return 'data:{type};base64,{encoded}'.format(
        type=type,
        encoded=encoded.replace('\n', '')
    )


def inline_file(fname):
    """Inline from a file source named ``fname``.
    """
    ext = os.path.splitext(fname)[1]  # ".png"
    return inline_data(
        open(fname, 'rb').read(),
        type='image/' + ext[1:],      # remove the dot
        name=fname
    )


def inline_url(uri):
    """Fetch ``uri`` and inline.
    """
    fp = urllib.urlopen(uri)
    return inline_data(
        fp.read(),
        type=fp.headers['Content-Type'],
        name=uri
    )


@task(
    default=True
)
def inline(ctx, fname):
    """Compile a file of inlines to data uris.

       The file should be named foo.less.inline, and contain a list
       of variables, i.e.::

           @foo: "http://.." ;
           @bar: "path/to/local/file.png";

       into::

           @foo: "data:image/png;base64,..."
           @bar: "data:image/png;base64,..."

       for all resources that are less than 10KB and writes the result
       to `foo.less` (i.e. the filname without the `.inline` extension).

       If the resource is too big, the original value is passed through,
       so if you specify a url it should always be safe (but slower to build).
    """
    lines = open(fname).readlines()
    output_fname = os.path.splitext(fname)[0]
    with open(output_fname, 'wb') as fp:
        for line in lines:
            if line.startswith('@'):
                varname, content = line.split(':', 1)
                content = content.strip().rstrip(';').strip("\"'")
                if re.match(r'^https?://', content):
                    data = inline_url(content)
                else:
                    data = inline_file(content)
                line = '{varname}: "{content}";\n'.format(
                    varname=varname,
                    content=data
                )
            fp.writelines([line])


@task
def list_urls(ctx, filename):
    """List all url(..) targets in the filename.
    """
    for match in re.findall(r'url\((.*?)\)', open(filename, 'rb').read()):
        print match
