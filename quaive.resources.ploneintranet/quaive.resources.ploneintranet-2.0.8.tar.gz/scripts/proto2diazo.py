#!/usr/bin/env python
# coding=utf-8
from os.path import join

import os
import logging
import re
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(sys.argv[0])

PROTO_DIR = join('release', 'prototype', '_site')
DIAZO_DIR = join('src', 'quaive', 'resources', 'ploneintranet', 'static')
DIAZO_RULES = join(DIAZO_DIR, 'rules.xml')
HREF_PATTERN = re.compile(r'href="generated/(.*)"')


def fix_urls(filename):
    ''' Fix the urls in filename
    '''
    logger.info("Rewriting resource URLs in %s", filename)
    path = join(PROTO_DIR, filename)
    target = join(DIAZO_DIR, 'generated', filename)
    try:
        with open(path) as f:
            content = f.read()
    except:
        logger.exception('Problem reading %s', path)
        return

    content = (
        content
        .replace(
            'src="/bundles/ploneintranet.js',
            'src="++theme++ploneintranet.theme/generated/bundles/ploneintranet.js'  # noqa
        )
        .replace(
            'http://demo.ploneintranet.net/',
            '++theme++ploneintranet.theme/generated/',
        )
        .replace(
            '="/media/',
            '="++theme++ploneintranet.theme/generated/media/'
        )
        .replace(
            '="/style/',
            '="++theme++ploneintranet.theme/generated/style/'
        )
        .replace(
            '="media/',
            '="++theme++ploneintranet.theme/generated/media/'
        )
        .replace(
            '="style/',
            '="++theme++ploneintranet.theme/generated/style/'
        )
        .replace(
            'url(/media/',
            'url(../media/'
        )
        .replace(
            'url(/style/',
            'url('
        )
    )
    try:
        os.makedirs(os.path.dirname(target))
    except OSError:
        if not os.path.isdir(os.path.dirname(target)):
            raise
    open(target, 'w').write(content)
    logger.info("Rewritten resource URLs in %s", filename)


def run():
    with open(DIAZO_RULES) as rules:
        filenames = HREF_PATTERN.findall(rules.read())
    map(fix_urls, filenames)
    logger.info('Done wit rules, doing styles now')
    fix_urls('style/screen.css')


if __name__ == '__main__':
    run()
