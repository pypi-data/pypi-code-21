#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..bcommon import default


class Config:
    Port = default.DEFAULT_PORT

    @staticmethod
    def set(args):
        Config.Port = args.port
