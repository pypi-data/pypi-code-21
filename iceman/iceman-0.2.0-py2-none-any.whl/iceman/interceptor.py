# -*- coding: utf-8 -*-
"""interceptor module
"""
import socket
import nfqueue

class Interceptor(object):
    """entrypoint to handle intercepted packets
    """

    @classmethod
    def intercept(cls, traffic):
        """decides networking packets defined by iptables

        :param traffic: egress/ingress class
        :type traffic: instance method
        """

        queue = nfqueue.queue()
        queue.set_callback(traffic.callback)
        queue.open()
        queue.create_queue(traffic.queue)
        try:
            queue.try_run()
        except KeyboardInterrupt:
            queue.unbind(socket.AF_INET)
            queue.close()
