import logging
import random
import time

import sepiida.backend

LOGGER = logging.getLogger(__name__)

@sepiida.backend.task(bind=True)
def do_sum(self, x, y): # pylint: disable=unused-argument
    LOGGER.info("Summing %d and %d", x, y)
    return sum([x, y])

def send_jobs():
    try:
        while True:
            x = random.randint(0, 100)
            y = random.randint(0, 100)
            LOGGER.info("Sending %d and %d", x, y)
            do_sum.delay(x=x, y=y)
            time.sleep(3)
    except KeyboardInterrupt:
        LOGGER.info("Shutting down")

APP = sepiida.backend.create('sepiida.testing',
    rabbit_url = 'amqp://guest:guest@localhost',
    flask_app = None,
)
