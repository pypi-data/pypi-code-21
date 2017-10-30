#!/usr/bin/env python
# -*- coding: utf-8 -*-
from argparse import ArgumentParser


def get_args():
    """
    Builds the argument parser
    :return: the argument parser
    :rtype: ArgumentParser
    """
    opts = ArgumentParser()

    settings_opt = opts.add_argument_group("Settings")
    settings_opt.add_argument("FILES_LOCATION", type=str,
                              help="what dir to scan")
    settings_opt.add_argument("-e", "--extensions", dest="extensions", nargs='*', type=str,
                              help="translate only this extensions")
    settings_opt.add_argument("-s", "--source", dest="source", type=str,
                              help="source language")
    settings_opt.add_argument("-t", "--target", dest="target", type=str, required=True,
                              help="target language")
    return opts


args_parse = get_args()
