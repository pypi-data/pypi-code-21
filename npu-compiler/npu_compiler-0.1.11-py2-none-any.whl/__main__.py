#!/usr/bin/python

import argparse

import npu_compiler
from npu_compiler.config import Config

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='gxnpuc', description='NPU Compiler')
    parser.add_argument('-V', '--version', action='version', version='gxnpuc %s' % Config.VERSION)
    parser.add_argument('--config', metavar='config_file', default='default_config.yaml',
                        help='config file (default: default_config.yaml)')
    args = parser.parse_args()
    npu_compiler.run(args.config)

    # use this config in version 1.0
    #parser.add_argument('config_filename',  help='config file')
    #npu_compiler.run(args.config_filename)
