# Benchmarking Suite
# Copyright 2014-2017 Engineering Ingegneria Informatica S.p.A.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Developed in the ARTIST EU project (www.artist-project.eu) and in the
# CloudPerfect EU project (https://cloudperfect.eu/)

import logging
import signal
import sys
import json

from flask import Flask
from flask_restplus import Swagger

from benchsuite.rest.apiv1 import blueprint as blueprint1
from benchsuite.rest.apiv1 import api as apiv1
app = Flask(__name__)


#app.config.SWAGGER_UI_JSONEDITOR = True
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'

app.register_blueprint(blueprint1)

def on_exit(sig, func=None):
    print('Bye bye...')
    sys.exit(1)


def dump_swagger_specs():
    app.config['SERVER_NAME'] = 'example.org:80'
    with app.app_context():
        print()
        with open('swagger-apiv1.json', 'w') as outfile:
            json.dump(Swagger(apiv1).as_dict(), outfile)


if __name__ == '__main__':

    signal.signal(signal.SIGINT, on_exit)

    logging.basicConfig(
        level=logging.DEBUG,
        stream=sys.stdout)

    if len(sys.argv) > 1 and sys.argv[1] == '--dump-specs':
        dump_swagger_specs()
        sys.exit(0)


    #TODO: use nginx here instead of the internal server
    print('Using internal server. Not use this in production!!!')
    app.run(debug=True)

