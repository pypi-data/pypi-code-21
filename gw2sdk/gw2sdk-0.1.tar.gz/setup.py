#! /usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='gw2sdk',
    version='0.1',
    scripts=['connectors/commerce.py',
             'connectors/items.py',
             'connectors/recipes.py']
)
