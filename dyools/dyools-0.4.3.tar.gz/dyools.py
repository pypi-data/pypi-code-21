#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import re
import sys
from contextlib import contextmanager

import click

try:
    basestring
except NameError:
    basestring = str

__VERSION__ = '0.4.3'
__AUTHOR__ = ''
__WEBSITE__ = ''
__DATE__ = ''


class Operator(object):
    @classmethod
    def flat(cls, *lists):
        result = []

        def put_in(item):
            if IF.is_iterable(item):
                for x in item:
                    put_in(x)
            else:
                result.append(item)

        for item in lists:
            put_in(item)
        return result

    @classmethod
    def unique(cls, sequence):
        result = []
        if IF.is_iterable(sequence):
            for item in sequence:
                found = False
                for res in result:
                    if res is item:
                        found = True
                        break
                if not found:
                    result.append(item)
        else:
            return sequence
        return result

    @classmethod
    def split_and_flat(cls, sep=',', *lists):
        result = cls.flat(lists)
        for i, item in enumerate(result):
            if IF.is_str(item):
                result[i] = item.split(sep)
        return cls.flat(result)

        def put_in(item):
            if IF.is_iterable(item):
                for x in item:
                    put_in(x)
            else:
                result.append(item)

        for item in lists:
            put_in(item)
        return result


class IF(object):
    @classmethod
    def is_xmlid(cls, text):
        if not cls.is_str(text) or cls.is_empty(text):
            return False
        else:
            text = text.strip()
            if re.match("^[a-z0-9_]+\.[a-z0-9_]+$", text):
                return True
            else:
                return False

    @classmethod
    def is_str(cls, text):
        if isinstance(text, basestring):
            return True
        else:
            return False

    @classmethod
    def is_empty(cls, text):
        if cls.is_str(text):
            text = text.strip()
        if text:
            return False
        else:
            return True

    @classmethod
    def is_iterable(cls, text):
        if cls.is_str(text):
            return False
        if hasattr(text, '__iter__'):
            return True
        else:
            return False


class Eval(object):
    def __init__(self, data, context):
        self.data = data
        self.context = context or {}

    def eval(self, eval_result=True):
        def parse(value, ctx):
            if isinstance(value, list):
                return [parse(item, ctx) for item in value]
            elif isinstance(value, dict):
                _d = {}
                for _k, _v in value.items():
                    _d[_k] = parse(_v, ctx)
                return _d
            elif isinstance(value, basestring):
                origin = value
                res = value.format(**ctx)
                if origin != res and eval_result:
                    try:
                        res = eval(res, ctx)
                    except Exception as e:
                        pass
                return res
            else:
                return value

        return parse(self.data, self.context)


class SFTP(object):
    def __init__(self, sftp):
        self.sftp = sftp

    @contextmanager
    def chdir(self, path):
        try:
            origin = self.sftp.getcwd()
            self.sftp.chdir(path)
            yield
        except Exception as e:
            raise e
        finally:
            self.sftp.chdir(origin)


class Path(object):
    @classmethod
    @contextmanager
    def chdir(cls, path):
        try:
            origin = os.getcwd()
            os.chdir(path)
            yield
        except Exception as e:
            raise e
        finally:
            os.chdir(origin)

    @classmethod
    def subpaths(self, path, isfile=False):
        elements = []
        sep = os.path.sep if path.startswith(os.path.sep) else ''
        res = [x for x in path.split(os.path.sep) if x]
        res.reverse()
        while res:
            item = res.pop()
            if elements:
                elements.append(os.path.join(sep, elements[-1], item))
            else:
                elements = [os.path.join(sep, item)]
        return elements if not isfile else elements[:-1]


class Logger(object):
    def _clean_msg(self, msg):
        if not isinstance(msg, basestring):
            try:
                msg = unicode(msg)
            except:
                try:
                    msg = str(msg)
                except:
                    pass
        return msg

    def info(self, msg, exit=False):
        click.echo(self._clean_msg(msg))
        if exit:
            sys.exit(-1)

    def warn(self, msg, exit=False):
        click.secho(self._clean_msg(msg), fg='yellow')
        if exit:
            sys.exit(-1)

    def debug(self, msg, exit=False):
        click.secho(self._clean_msg(msg), fg='blue')
        if exit:
            sys.exit(-1)

    def success(self, msg, exit=False):
        click.secho(self._clean_msg(msg), fg='green')
        if exit:
            sys.exit(-1)

    def code(self, msg, exit=False):
        click.secho(self._clean_msg(msg), fg='cyan')
        if exit:
            sys.exit(-1)

    def error(self, msg, exit=True):
        click.secho(self._clean_msg(msg), fg='red')
        if exit:
            sys.exit(-1)

    def error(self, msg, exit=False):
        click.secho(self._clean_msg(msg), fg='red')
        if exit:
            sys.exit(-1)

    def title(self, msg, exit=False):
        click.secho(self._clean_msg(msg), fg='white', bold=True)
        if exit:
            sys.exit(-1)
