# -*- coding: utf-8 -*-
import os
import hashlib

from dkfileutils.path import Path
from dktasklib.wintask import task
from invoke import Collection
from dktasklib.concat import copy
from .package import Package


@task(
    default=True,
    autoprint=True,     # print return value
)
def version(ctx):
    """Print this package's version number.
    """
    return Package().version


def min_name(fname, min='.min'):
    """Adds a `.min` extension before the last file extension.
    """
    name, ext = os.path.splitext(fname)
    return name + min + ext


def versioned_name(fname):
    """Returns a template string containing `{version}` in the correct
       place.
    """
    if '.min.' in fname:
        pre, post = fname.split('.min.')
        return pre + '-{version}.min.' + post
    else:
        return min_name(fname, '-{version}')

version_name = versioned_name


def get_version(ctx, fname, kind='pkg'):
    """Return the version number for fname.
    """
    fname = Path(fname)
    if kind == "pkg":
        return ctx.pkg.version
    elif kind == "hash":
        md5 = fname.dirname() / '.md5'
        if md5.exists():
            return md5.open().read()
        return hashlib.md5(open(fname).read()).hexdigest()
    # elif kind == "svn":
    #     ver = get_svn_version(source)
    return ""


# @task(help=dict(
#     source="",
#     dest_template="this filename template must contain '{version}'",
#     kind="type of version number [pkg,hash]",
# ))
def copy_to_version(ctx, source, outputdir=None, kind="pkg", force=False):
    """Copy source with version number to `outputdir`.

       The version type is specified by the ``kind`` parameter and can be
       either "pkg" (package version), "svn" (current subversion revision
       number), or "hash" (the md5 hash of the file's contents).

       Returns:
           (str) output file name
    """
    # where to place the versioned file..
    source = Path(source)
    outputdir = Path(outputdir) if outputdir else source.dirname()
    outputdir.makedirs()
    dst_fname = source.basename()
    if '{version}' not in str(dst_fname):
        dst_fname = versioned_name(dst_fname)
    dst = outputdir / dst_fname.format(version=get_version(ctx, source, kind))

    if force or not os.path.exists(dst):
        copy(ctx, source, dst, force=force)

    elif open(source).read() != open(dst).read():
        print """
        Filename already exists, add --force or call upversion: {}
        """.format(dst)

    return dst

add_version = copy_to_version


ns = Collection(
    'version',
    version,
)
ns.configure({
    'force': False,
    'pkg': {
        'name': '<package-name>',
        'version': '<version-string>',
    },
})
