#!/usr/bin/env python
# -*- coding: utf-8 -*-

import importlib

import nltk


try:
    _translator = importlib.import_module('caighdean.translator')
except LookupError:
    nltk.download('perluniprops')
    _translator = importlib.import_module('caighdean.translator')
Translator = _translator.Translator


__all__ = ["Translator"]
