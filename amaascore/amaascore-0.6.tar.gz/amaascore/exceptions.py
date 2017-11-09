from __future__ import absolute_import, division, print_function, unicode_literals


class AMaaSException(Exception):
    """ Base class for all AMaaS Exceptions """
    pass


class TransactionNeedsSaving(Exception):
    def __init__(self):
        message = "Transaction needs to be saved to AMaaS Core for the functionality to be valid"
        super(TransactionNeedsSaving, self).__init__(message)
