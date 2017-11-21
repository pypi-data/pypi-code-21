#
# A library to manage ARCFIRE experiments
#
#    Copyright (C) 2017 Nextworks S.r.l.
#    Copyright (C) 2017 imec
#
#    Sander Vrijders   <sander.vrijders@ugent.be>
#    Dimitri Staessens <dimitri.staessens@ugent.be>
#    Vincenzo Maffione <v.maffione@nextworks.it>
#    Marco Capitani    <m.capitani@nextworks.it>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., http://www.fsf.org/about/contact/.
#

import time

import rumba.log as log
import rumba.model as model

# Fix Python 2.x.
try:
    input = raw_input
except NameError:
    pass

logger = log.get_logger(__name__)


class ExperimentManager(object):

    PROMPT = 1
    AUTO = 2
    NO = 3

    def __init__(self, experiment, do_swap_out=AUTO):
        assert isinstance(experiment, model.Experiment), \
            'An experiment instance is required.'
        self.experiment = experiment
        self.do_swap_out = do_swap_out

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.do_swap_out == self.PROMPT:
            logger.info('Press ENTER to start swap out.')
            input('')
        if self.do_swap_out == self.PROMPT \
                or self.do_swap_out == self.AUTO:
            self.experiment.swap_out()
        if exc_val is not None:
            logger.error('Something went wrong. Got %s: %s',
                         type(exc_val).__name__, str(exc_val))
            logger.debug('Exception details:', exc_info=exc_val)
        time.sleep(0.1)  # Give the queue logger enough time to flush.
        return True  # Suppress the exception we logged: no traceback.
