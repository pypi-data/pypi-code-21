###############################################################################
#
#   Copyright: (c) 2017 Carlo Sbraccia
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
###############################################################################

from ..routerlib import DataRouter
from ..routerlib import RegistrationHandler, BbgBDPHandler, BbgBDHHandler

from onyx.core.utils.logging import setup_logging_from_json_config

import logging
import argh

fmtstr = "%(asctime)-15s %(levelname)-8s %(message)s"
logging.basicConfig(level=logging.DEBUG, format=fmtstr)


# -----------------------------------------------------------------------------
def run(port=None, logging_config_file=None):
    setup_logging_from_json_config(logging_config_file)
    logger = logging.getLogger(__name__)
    handlers = [
        (r"/register/", RegistrationHandler),
        (r"/bbg-bdp/", BbgBDPHandler),
        (r"/bbg-bdh/", BbgBDHHandler),
    ]
    router = DataRouter(handlers=handlers, logger=logger)
    router.start(port)


# -----------------------------------------------------------------------------
def main():
    argh.dispatch_command(run)


# -----------------------------------------------------------------------------
#  for interactive use
if __name__ == "__main__":
    run()
