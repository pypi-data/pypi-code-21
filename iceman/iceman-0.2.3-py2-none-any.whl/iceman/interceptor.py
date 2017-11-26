# -*- coding: utf-8 -*-
"""interceptor module
"""
from netfilterqueue import NetfilterQueue #pylint: disable=no-name-in-module

class Interceptor(object):
    """entrypoint to handle intercepted packets
    """

    @classmethod
    def intercept(cls, traffic):
        """decides networking packets defined by iptables

        :param traffic: egress/ingress class
        :type traffic: instance method
        """

        queue = NetfilterQueue()
        queue.bind(traffic.queue, traffic.callback)
        try:
            queue.run()
        except KeyboardInterrupt:
            queue.unbind()
            queue.close()
