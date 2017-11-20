#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess


class Version:
    def __init__(self, frozen):
        self._get_hash(frozen)
        self._get_string(frozen)
        self._get_url(frozen)
        self._get_token(frozen)
        self._get_text(frozen)

    def _get_hash(self, frozen):
        if frozen:
            self.hash = frozen.hg_hash
        else:
            path = os.path.dirname(os.path.dirname(__file__))
            try:
                pipe = subprocess.Popen(['hg', 'id', '-i', '-R', path], stdout=subprocess.PIPE)
                self.hash = pipe.stdout.read().decode()
            except OSError:
                self.hash = 'unknown'
        self.hash = self.hash.strip()

    def _get_string(self, frozen):
        if frozen:
            self.string = frozen.version
        else:
            self.string = '0.0.0'

    def _get_url(self, frozen):
        if frozen:
            self.url = frozen.url
        else:
            self.url = ''

    def _get_token(self, frozen):
        if frozen:
            self.token = frozen.token
        else:
            self.token = ''

    def _get_text(self, frozen):
        if frozen:
            self.text = frozen.text
        else:
            self.text = ''
