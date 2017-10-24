from evosnap import constants
from evosnap.transactions.mixins import TransactionRequestMixin


class Request(TransactionRequestMixin):
    def __init__(self, **kwargs):
        """
        Basic information about the check being processed. This element is Required.
        :param activation: Contains information for activating an account. This is a required element.
        """
        super(Request, self).__init__(**kwargs)