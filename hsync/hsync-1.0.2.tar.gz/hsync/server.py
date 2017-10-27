#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os
import pickle

from flask import Flask, request
from werkzeug.routing import BaseConverter

from hsync.file import ServerDir, File


class RegexConverter(BaseConverter):
    def __init__(self, _map, *args):
        super(RegexConverter, self).__init__(_map)
        self.map = map
        self.regex = args[0]


app = Flask(__name__)

app.url_map.converters['regex'] = RegexConverter


def _parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--port', default=6688, help='http server bind port default: 6688')

    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s 1.0.1',
    )
    return parser.parse_args()


@app.route('/<regex("([\/\w-]+)*$"):root_path>', methods=['GET'])
def get(root_path):
    root_path = '/' + root_path
    server_dir = ServerDir(root_path, (), ())
    return pickle.dumps(server_dir.get_file_list())


@app.route('/<regex("([\/\w-]+)*$"):root_path>', methods=['POST'])
def post(root_path):
    root_path = '/' + root_path
    os.chdir(root_path)
    file_data = request.get_data()
    f = File.from_json(file_data)
    f.write_file()
    return 'success!'


def main():
    args = _parse_args()
    app.run(host='0.0.0.0', debug=False, port=args.port)


if __name__ == '__main__':
    main()