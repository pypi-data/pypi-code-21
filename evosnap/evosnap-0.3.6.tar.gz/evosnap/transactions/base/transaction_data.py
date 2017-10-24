import datetime

from evosnap import constants
from evosnap.transactions.bankcard import InternetTransactionData
from evosnap.transactions.enum import TransactionDataType, IndustryType, CustomerPresent, EntryMode, AccountType, \
    GoodsType


class TransactionData:
    def __init__(self, amount, currency_code, campaign_id=None, reference=None,
                 transaction_date_time=None, customer_present:CustomerPresent=CustomerPresent.not_set,
                 entry_mode:EntryMode=EntryMode.not_set, order_number=None, signature_captured=False,
                 account_type:AccountType=AccountType.not_set, alternative_merchant_data=None, approval_code=None,
                 batch_assignment=None, batch_id=None, cash_back_amount=None, employee_id=None, fee_amount=None,
                 goods_type:GoodsType=GoodsType.not_set, industry_type:IndustryType=IndustryType.not_set,
                 internet_transaction_data:InternetTransactionData=None, invoice_number=None, is_partial_shipment=None,
                 is_quasi_cash=None, lane_id=None, partial_approval_capable=None, score_threshold=None,
                 terminal_id=None, tip_amount=None, transaction_code=None,
                 transaction_data_type:TransactionDataType=None, is_3_d_secure=None):
        """
        Base class object containing information for a specific transaction. This element is Required.
        :param activation: Contains information for activating an account. This is a required element.
        """
        self.__camelcase=constants.ALL_FIELDS
        self.__order=[]

        if transaction_data_type:
            self.i_type = transaction_data_type
            self.__order.append('$type')
        self.amount=amount
        self.__order.append('Amount')
        if campaign_id:
            self.campaign_id=campaign_id
            self.__order.append('CampaignId')
        self.currency_code=currency_code
        self.__order.append('CurrencyCode')
        if reference:
            self.reference=reference
            self.__order.append('Reference')
        self.transaction_date_time=transaction_date_time or datetime.datetime.now().isoformat()
        self.__order.append('TransactionDateTime')
        if transaction_code:
            self.transaction_code=transaction_code
            self.__order.append('TransactionCode')
        self.account_type=account_type
        self.__order.append('AccountType')
        if alternative_merchant_data:
            self.alternative_merchant_data=alternative_merchant_data
            self.__order.append('AlternativeMerchantData')
        self.approval_code=approval_code
        self.__order.append('ApprovalCode')
        if batch_assignment:
            self.batch_assignment=batch_assignment
            self.__order.append('BatchAssignment')
        if batch_id:
            self.batch_id=batch_id
            self.__order.append('BatchId')
        self.cash_back_amount=cash_back_amount if cash_back_amount else '0.00'
        self.__order.append('CashBackAmount')
        self.customer_present=customer_present
        self.__order.append('CustomerPresent')
        self.employee_id=employee_id
        self.__order.append('EmployeeId')
        self.entry_mode=entry_mode
        self.__order.append('EntryMode')
        self.fee_amount=fee_amount if fee_amount else '0.00'
        self.__order.append('FeeAmount')
        self.goods_type=goods_type
        self.__order.append('GoodsType')
        self.industry_type=industry_type
        self.__order.append('IndustryType')
        self.internet_transaction_data=internet_transaction_data
        self.__order.append('InternetTransactionData')
        self.invoice_number=invoice_number
        if is_3_d_secure:
            self.is_3_d_secure=is_3_d_secure
            self.__order.append('Is3DSecure')
        self.__order.append('InvoiceNumber')
        if is_partial_shipment:
            self.is_partial_shipment=is_partial_shipment
            self.__order.append('IsPartialShipment')
        if is_quasi_cash:
            self.is_quasi_cash=is_quasi_cash
            self.__order.append('IsQuasiCash')
        if lane_id:
            self.lane_id=lane_id
            self.__order.append('LaneId')
        self.order_number=order_number
        self.__order.append('OrderNumber')
        if partial_approval_capable:
            self.partial_approval_capable=partial_approval_capable
            self.__order.append('PartialApprovalCapable')
        if score_threshold:
            self.score_threshold=score_threshold
            self.__order.append('ScoreThreshold')
        self.signature_captured=signature_captured
        self.__order.append('SignatureCaptured')
        if terminal_id:
            self.terminal_id=terminal_id
            self.__order.append('TerminalId')
        self.tip_amount=tip_amount if tip_amount else '0.00'
        self.__order.append('TipAmount')
