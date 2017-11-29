# -*- coding: utf-8 -*-

"""Move a symbolic link to another directory, adjusting the link contents."""

__author__ = """Eugene M. Kim"""
__email__ = 'astralblue@gmail.com'
__version__ = '0.1.0'

import argparse
import errno
import logging
import os
import os.path
import stat
import sys

logger = logging.getLogger(__name__)


class ArgumentError(RuntimeError):
    """An invalid argument was given.

    `~BaseException.args` contain (*desc*, *src*, *dst*), where:

    - *desc* is a human-readable description of the nature of the error;
    - *src* is the source symbolic link;
    - *dst* is the destination.
    """


class OperationError(RuntimeError):
    """An underlying operation failed.

    :py:attr:`~BaseException.args` contain (*desc*), where *desc* is a
    human-readable description of the failed operation.

    The `__cause__` attribute may contains the underlying root cause exception;
    it is often an `OSError`.
    """


def _do(action, descr):
    logger.debug(descr)
    try:
        return action()
    except Exception as e:
        raise OperationError("cannot {}: {}".format(descr, e)) from e


def _fsdecode(path):
    return _do(lambda: os.fsdecode(path), "normalize path {!r}".format(path))


def _isdir(path):
    return _do(lambda: os.path.isdir(path),
               "check if {!r} is a directory".format(path))


def _unlink_if_exists(path):
    try:
        _do(lambda: os.unlink(path), "unlink {!r}".format(path))
    except OperationError as e:
        cause = e.__cause__
        if isinstance(cause, OSError) or cause.errno != errno.ENOENT:
            raise


def move_symlink(src, dst):
    """Move a symbolic link to another directory, adjusting the link contents.

    :param src: source symbolic link.
    :type src: a :term:`path-like object`
    :param dst:
        destination; must either not exist or be an existing directory.  If an
        existing directory, move the source symbolic link is into the
        directory, keeping the same basename.
    :type dst: a :term:`path-like object`
    :raise `ArgumentError`: if *src* or *dst* is invalid.
    :raise `OperationError`: if an underlying operation fails.
    """
    src0 = src
    dst0 = dst
    src = _fsdecode(src0)
    dst = _fsdecode(dst0)
    srclink = _do(lambda: os.readlink(src), "readlink {!r}".format(src))
    srcdir = os.path.dirname(src) or '.'
    srcbase = os.path.basename(src)
    assert srcbase
    dstdir = os.path.dirname(dst) or '.'
    dstbase = os.path.basename(dst)
    logger.debug("src={!r}, srcdir={!r}, srcbase={!r}, "
                 "dst={!r}, dstdir={!r}, dstbase={!r}"
                 .format(src, srcdir, srcbase, dst, dstdir, dstbase))
    if _isdir(dst):
        dst = os.path.join(dst, srcbase)
        dstbase = os.path.basename(dst)
        dstdir = os.path.dirname(dst)
        assert dstbase == srcbase
        logger.debug("assuming dstbase=srcbase; "
                     "now dst={!r}, dstdir={!r}, dstbase={!r}"
                     .format(dst, dstdir, dstbase))
    if not _isdir(dstdir):
        raise ArgumentError("destination {!r} does not exist "
                            "or is not a directory"
                            .format(dstdir), src0, dst0)
    logger.debug("dstdir exists")
    if os.path.samefile(srcdir, dstdir) and srcbase == dstbase:
        raise ArgumentError("source {!r} and destination {!r} "
                            "refer to the same location"
                            .format(src, dst), src0, dst0)
    if os.path.isabs(srclink):
        dstlink = srclink
    else:
        srcreal = _do(lambda: os.path.realpath(src),
                      "obtain realpath for {!r}".format(src))
        dstlink = os.path.relpath(srcreal, dstdir)
    logger.debug("srclink={!r}, dstlink={!r}".format(srclink, dstlink))
    srcstat = _do(lambda: os.stat(src, follow_symlinks=False),
                  "stat {!r}".format(src))
    _do(lambda: os.symlink(dstlink, dst),
        "symlink {!r} -> {!r}".format(dst, dstlink))
    try:
        if os.geteuid() == 0:
            _do(lambda: os.chown(dst, srcstat.st_uid, srcstat.st_gid,
                                 follow_symlinks=False),
                "chown {!r} to {!r}:{!r}"
                .format(dst, srcstat.st_uid, srcstat.st_gid))
        srcmode = stat.S_IMODE(srcstat.st_mode)
        _do(lambda: os.chmod(dst, srcmode, follow_symlinks=False),
            "chmod {!r} to {:#o}".format(dst, srcmode))
        _unlink_if_exists(src)
    except Exception:
        _unlink_if_exists(dst)
        raise


def main():
    """Run this module as a command."""
    parser = argparse.ArgumentParser()
    logging.basicConfig(format=("{}: %(levelname)s: %(message)s"
                                .format(parser.prog)))
    logger.setLevel(logging.WARNING)
    parser.add_argument('--debug', action='store_const', const=True,
                        help="""enable debugging""")
    parser.add_argument('src', help="""source symbolic link""")
    parser.add_argument('dst', help="""destination symbolic link""")
    parser.set_defaults(debug=False)
    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
    try:
        move_symlink(args.src, args.dst)
    except OperationError as e:
        if args.debug:
            logger.critical(e, exc_info=e)
        else:
            logger.critical(e)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
