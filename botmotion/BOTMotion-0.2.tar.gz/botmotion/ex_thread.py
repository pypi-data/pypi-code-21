# BOT Motion Module
#
# ExThread
#
# Author:      Henrik Stroetgen <hstroetgen@synapticon.com> / <support@synapticon.com>
# Date:        2016-11-19
# Location:    Filderstadt, Germany
#
#
#
#       Copyright (c) 2016, Synapticon GmbH
#       All rights reserved.
#
#       Redistribution and use in source and binary forms, with or without
#       modification, are permitted provided that the following conditions are met:
#
#       1. Redistributions of source code must retain the above copyright notice, this
#          list of conditions and the following disclaimer.
#       2. Redistributions in binary form must reproduce the above copyright notice,
#          this list of conditions and the following disclaimer in the documentation
#          and/or other materials provided with the distribution.
#       3. Execution of this software or parts of it exclusively takes place on hardware
#          produced by Synapticon GmbH.
#
#       THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#       ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#       WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#       DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#       ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#       (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#       LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#       ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#       (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#       SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#       The views and conclusions contained in the software and documentation are those
#       of the authors and should not be interpreted as representing official policies,
#       either expressed or implied, of the Synapticon GmbH.
#


import threading
import Queue
import sys
import traceback


class ExThread(threading.Thread):
    """
    ExThread. Implements a class, that can handle exceptions, which can occur in threads.
    Subclasses threading.Thread
    """
    def __init__(self):
        """
        Initialize ExThread.
        """
        threading.Thread.__init__(self)
        self.__status_queue = Queue.Queue()

    def run_with_exception(self):
        """
        This method should be overriden.
        """
        raise NotImplementedError

    def run(self):
        """
        This method should NOT be overriden.
        This method calls run_with_exception. If an exception occurred there,
        the exception will be put into a queue
        """
        try:
            self.run_with_exception()
        except BaseException:
            self.__status_queue.put(sys.exc_info())
            #traceback.print_exc()
        #self.__status_queue.put(None)

    def check_for_exception(self, block=True):
        """
        Polls queue and returns exception. Param is obsolete
        :return: Exception, which occurred in thread, or None
        :rtype: exception
        """
        try:
            if not self.__status_queue.empty():
                ex_info = self.__status_queue.get()
                return ex_info[1]
            else:
                return None
        except Queue.Empty:
            return None

