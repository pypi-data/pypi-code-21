from collections import OrderedDict
from django.conf import settings

# Dragonpay status codes
# See Appendix 3 of Dragonpay API documentation
DRAGONPAY_STATUS_CODES = {
    'S': 'Success',
    'F': 'Failed',
    'P': 'Pending',
    'U': 'Unknown',
    'R': 'Refund',
    'K': 'Chargeback',
    'V': 'Voided',
    'A': 'Authorized',
    'G': 'In progress',
}

# Dragonpay error codes.
# See Appendix 2 of Dragonpay API documentation
DRAGONPAY_ERROR_CODES = {
    '000': 'Success',
    '101': 'Invalid payment gateway id',
    '102': 'Incorrect secret key',
    '103': 'Invalid reference number',
    '104': 'Unauthorized access',
    '105': 'Invalid token',
    '106': 'Currency not supported',
    '107': 'Transaction cancelled',
    '108': 'Insufficient funds',
    '109': 'Transaction limit exceeded',
    '110': 'Error in operation',
    '111': 'Invalid parameters',
    '201': 'Invalid Merchant Id',
    '202': 'Invalid Merchant Password'
}


DRAGONPAY_PAYOUT_ERROR_CODES = {
    '0': 'Successfully created payout request',
    '-1': 'Invalid credentials or apiKey',
    '-2': '(reserved)',
    '-3': '(reserved)',
    '-4': 'Unable to create payout transaction (internal error)',
    '-5': 'Invalid account no / details',
    '-6': 'Invalid pre-dated run date',
    '-7': 'Amount exceeds limit for payout channel',
    '-8': 'A payout has been previously requested for the same merchant txn id',
    '-9': 'Source IP Address not whitelisted.'
}


DRAGONPAY_PAYMENT_METHODS = {
    'otc_bank': OrderedDict([
        ('BOGX', 'Bogus Bank Over-the-Counter'),
        ('BDOA', 'Banco de Oro ATM'),
        ('BDRX', 'BDO Cash Deposit'),
        ('BPXB', 'BPI Bills Payment'),
        ('MBTX', 'Metrobank Cash/Check Payment'),
        ('CBCX', 'Chinabank ATM/Cash Payment'),
        ('EWBX', 'EastWest Online/Cash/Check Payment'),
        ('LBXB', 'Landbank Cash Payment'),
        ('PNBB', 'PNB e-Banking Bills Payment'),
        ('PNXB', 'PNB Cash Payment'),
        ('RCXB', 'RCBC Cash Payment'),
        ('RSXB', 'RCBC Savings Cash Payment'),
        ('SBCA', 'Security Bank ATM Bills Payment'),
        ('SBCB', 'Security Bank Cash Payment'),
        ('UBXB', 'Unionbank Cash Payment'),
        ('UCXB', 'UCPB ATM/Cash Payment'),
    ]),
    'online_bank': OrderedDict([
        ('BOG', 'Bogus Bank'),
        ('BDO', 'BDO Internet Banking'),
        ('BPI', 'BPI Express Online (Fund Transfer)'),
        ('BPIB', 'BPI Express Online (Bills Payment)'),
        ('MBTC', 'Metrobank Direct Online'),
        ('CBC', 'Chinabank Online'),
        ('LBPA', 'Landbank iAccess'),
        ('RCBC', 'RCBC Online Banking'),
        ('UBP', 'UnionBank eBanking'),
        ('UCPB', 'UCPB Connect'),
    ]),
    'others': OrderedDict([
        ('BAYD', 'Bayad Center'),
        ('LBC', 'LBC'),
        ('SMR', 'SM Dept/Supermarket/Savemore Counter'),
        ('CEBL', 'Cebuana Lhuillier Bills Payment'),
        ('MLH', 'M. Lhuillier'),
        ('RDS', 'Robinsons Dept Store'),
        ('ECPY', 'ECPay (Pawnshops, Payment Centers)'),
        ('RLNT', 'RuralNet Banks and Coops'),
    ])
}

if not settings.DRAGONPAY_TEST_MODE:
    # Remove Bogus Bank from the Available Payment Methods
    DRAGONPAY_PAYMENT_METHODS['online_bank'].pop('BOG')
    DRAGONPAY_PAYMENT_METHODS['otc_bank'].pop('BOGX')

# Account number for supported PAYOUT channels
ACCOUNT_NUMBER_LENGTHS = {
    'BDO': 10, 'BPI': 10, 'CBC': 10, 'EWB': 12, 'LBP': 10,
    'MBTC': 13, 'RCBC': 10, 'SBC': 13, 'UBP': 12, 'UCPB': 12
}

ACCOUNT_NUMBER_REGEX = {
    'BDO': r'^(00)?\d{10}$', 'BPI': r'^\d{10}$', 'CBC': r'^\d{10}$',
    'EWB': r'^\d{12}$', 'LBP': r'^\d{10}$', 'MBTC': r'^\d{13}$',
    'RCBC': r'^\d{10}$', 'SBC': r'^\d{13}$', 'UBP': r'^\d{12}$',
    'UCPB': r'^\d{12}$'
}


# Dragonpay Paymemnt method FILTERS
ONLINE_BANKING = 1       # Online banking
OTC_BANK = 2             # Over-the-Counter Banking and ATM
OTC_NON_BANK = 4         # Over-the-Counter non-Bank
# 8 (unused)
# 16 (reserved internally)
PAYPAL = 32              # PayPal
CREDIT_CARDS = 64        # Credit Cards
MOBILE = 128             # Mobile (Gcash)
INTERNATIONAL_OTC = 256  # International OTC
