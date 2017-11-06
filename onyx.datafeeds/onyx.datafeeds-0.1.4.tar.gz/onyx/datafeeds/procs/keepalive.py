###############################################################################
#
#   Copyright: (c) 2015 Carlo Sbraccia
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

from ..clients import DataClient
from ..exceptions import NoDataserverAvailable

from onyx.core.utils.logging import setup_logging_from_json_config

import logging
import time
import argh


# -----------------------------------------------------------------------------
def run(ticker="USDEUR CURNCY",
        keepalive_interval=120, logging_config_file=None):
    setup_logging_from_json_config(logging_config_file)
    logger = logging.getLogger(__name__)
    clt = DataClient()
    while True:
        try:
            clt.BDP(ticker, "PX_LAST")
        except NoDataserverAvailable as err:
            logger.info(err)
        except:
            logger.error("connection to datafeed "
                         "server is not working", exc_info=True)
        else:
            logger.info("conection to datafeed server is alive")

        time.sleep(keepalive_interval)


# -----------------------------------------------------------------------------
def main():
    argh.dispatch_command(run)


# -----------------------------------------------------------------------------
#  for interactive use
if __name__ == "__main__":
    run()
