#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from file import ServerDir, File
from flask import Flask, request
import pickle
from werkzeug.routing import BaseConverter


class RegexConverter(BaseConverter):
    def __init__(self, _map, *args):
        super(RegexConverter, self).__init__(_map)
        self.map = map
        self.regex = args[0]


app = Flask(__name__)

app.url_map.converters['regex'] = RegexConverter


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


def run():
    app.run(host='0.0.0.0', debug=True, port=6688)


if __name__ == '__main__':
    run()