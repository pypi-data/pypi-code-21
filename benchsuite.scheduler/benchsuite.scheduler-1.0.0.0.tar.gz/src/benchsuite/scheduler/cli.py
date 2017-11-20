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
import argparse
import logging
import signal
import time
import sys

import os

from benchsuite.scheduler import config
from benchsuite.scheduler.bsscheduler import get_bsscheduler, create_bsscheduler
from benchsuite.scheduler.config import BenchsuiteSchedulerConfig

logger = logging.getLogger(__name__)

def on_exit(sig, func=None):
    get_bsscheduler().shutdown()
    print('Bye bye...')
    sys.exit(1)



def get_config_parameters(config_file, use_env=True):

    cfg = {}
    if config_file:

        # config file format:
        # PARAM = VALUE

        with open(config_file) as f:
            lines = f.readlines()

        for l in lines:
            tokens = l.split('=')
            cfg[tokens[0].strip()] = tokens[1].strip()

    if use_env:

        for k in config.DEFAULTS.keys():
            if k in os.environ:
                cfg[k] = os.environ[k]

    return cfg




def main(args=None):

    signal.signal(signal.SIGINT, on_exit)

    logging.basicConfig(
        format='%(asctime)s - %(levelname)-7s %(message)s',
        level=logging.DEBUG,
        stream=sys.stdout)

    logging.getLogger('apscheduler').setLevel(logging.WARN)

    logger.info('Logging configured')


    parser = argparse.ArgumentParser(prog='benchsuite-scheduler')
    parser.add_argument('--config', '-c', type=str, help='the location of the config file')


    args = parser.parse_args(args = args)

    if args.config and not os.path.isfile(args.config):
        logger.info('Configuration file {0} does not exist. Do not considering it'.format(args.config))
        args.config = None

    config = get_config_parameters(args.config)



    bsscheduler = create_bsscheduler(BenchsuiteSchedulerConfig(config))
    bsscheduler.initialize()
    bsscheduler.start()

    # wait for the APScheduler thread finishes. This will happen when the
    # scheduler is shut down from a SIGINT (see on_exit function)
    #bsscheduler.scheduler._thread.join()

    bsscheduler.wait_unitl_shutdown()


if __name__ == '__main__':
    main(sys.argv[1:])