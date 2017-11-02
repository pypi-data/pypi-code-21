from django.conf import settings

SECRET_KEY = getattr(settings, 'SECRET_KEY')
# DRAGONPAY API
DRAGONPAY_TEST_MODE = getattr(settings, 'DRAGONPAY_TEST_MODE', False)
DRAGONPAY_ID = getattr(settings, 'DRAGONPAY_ID')
DRAGONPAY_PASSWORD = getattr(settings, 'DRAGONPAY_PASSWORD')
DRAGONPAY_API_KEY = getattr(settings, 'DRAGONPAY_API_KEY')
DRAGONPAY_ENCRYPT_PARAMS = getattr(settings, 'DRAGONPAY_ENCRYPT_PARAMS', False)

# the transaction length, max 40
DRAGONPAY_TXN_LENGTH = getattr(settings, 'DRAGONPAY_TXN_LENGTH', 20)
DRAGONPAY_SAVE_DATA = getattr(settings, 'DRAGONPAY_SAVE_DATA', False)

if DRAGONPAY_TEST_MODE:
    DRAGONPAY_BASE_URL = 'https://test.dragonpay.ph/'
    DRAGONPAY_PAYOUT_BASE_URL = 'https://test.dragonpay.ph/'
else:
    DRAGONPAY_BASE_URL = 'https://gw.dragonpay.ph/'
    DRAGONPAY_PAYOUT_BASE_URL = 'https://live.dragonpay.ph/'

# Other Dragonpay URLs
DRAGONPAY_PAY_URL = DRAGONPAY_BASE_URL + 'Pay.aspx'
DRAGONPAY_MERCHANT_URL = DRAGONPAY_BASE_URL + 'MerchantRequest.aspx'
DRAGONPAY_SOAP_URL = DRAGONPAY_BASE_URL + 'DragonpayWebService/MerchantService.asmx'
DRAGONPAY_PAYOUT_URL = DRAGONPAY_PAYOUT_BASE_URL + 'DragonpayWebService/PayoutService.asmx'
