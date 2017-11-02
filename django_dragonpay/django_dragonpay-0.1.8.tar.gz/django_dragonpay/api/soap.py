import json
import urllib
import logging
import requests
from lxml import etree
from datetime import datetime

from django.template.loader import render_to_string

from django_dragonpay.models import *
from django_dragonpay.utils import encrypt_data, generate_txn_id
from django_dragonpay import settings as dp_settings
from django_dragonpay.constants import (
    DRAGONPAY_STATUS_CODES, DRAGONPAY_ERROR_CODES,
    DRAGONPAY_PAYOUT_ERROR_CODES)
from django_dragonpay.exceptions import DragonpayException, ParamTooLong

logger = logging.getLogger('dragonpay')

HEADERS = {'Content-Type': 'text/xml; charset=utf-8'}
# constant context containinig api keys and passwords
CONTEXT = {
    'dp_merchant_id': dp_settings.DRAGONPAY_ID,
    'dp_merchant_apikey': dp_settings.DRAGONPAY_API_KEY,
    'dp_merchant_secret': dp_settings.DRAGONPAY_PASSWORD,
}


def _dragonpay_soap_wrapper(
        webmethod, context={}, xml_name=None, payout=False):
    '''Helper function for SOAP requests to DragonPay Payment Switch (PS).

    webmethod (string) - the DragonPay SOAP web method being called.
    context (dict) - the context to be passed to the XML template
    xml_name (string) - override filename for the XML template file to
        be used, if None, then webmethod.xml will be used.
    payout (boolean) - flag to use the DRAGONPAY_PAYOUT_URL.'''

    # include the configuration constants
    context.update(CONTEXT)
    context['web_method'] = webmethod

    xml = render_to_string(
        'dragonpay_soapxml/%s.xml' % xml_name or webmethod, context)

    headers = {'SOAPAction': "http://api.dragonpay.ph/%s" % webmethod}
    headers.update(HEADERS)

    # check if this is a PAYOUT transaction
    if not payout:
        url = dp_settings.DRAGONPAY_SOAP_URL
    else:
        url = dp_settings.DRAGONPAY_PAYOUT_URL

    logger.debug(
        'Sending SOAP Request to [%s]:\nHEADERS: %s\nXML:\n%s',
        url, headers, xml)
    response = requests.post(url, data=xml, headers=headers)

    try:
        xmltree = etree.fromstring(response.content)
    except etree.XMLSyntaxError:
        # Failed to create an XML object from response.content
        logger.error(
            'Failed to parse reponse as a valid XML: %s', response.content)
        return
    else:
        xml_pretty = etree.tostring(xmltree, pretty_print=True)

    if response.status_code != 200:
        logger.error(
            'Invalid response %s:\n%s', response.status_code, xml_pretty)
        raise DragonpayException(
            '[%d] Dragonpay %s request failed' % (
                response.status_code, webmethod))
    else:
        logger.debug('Success\n%s', xml_pretty)
        return xmltree


def _dragonpay_get_wrapper(webmethod, xml_name=None, context={}, payout=False):
    '''Dragonpay SOAP helper function that returns the result of
    GET WebMethods.'''

    xml_name = xml_name or webmethod
    xmltree = _dragonpay_soap_wrapper(webmethod, context, xml_name, payout)

    # Parse the response XML for the WebMethod specific response
    if xmltree is not None:
        response = xmltree.find(
            './/{http://api.dragonpay.ph/}%(webmethod)sResponse/'
            '{http://api.dragonpay.ph/}%(webmethod)sResult' % {
                'webmethod': webmethod}
        ).text

        return response


def get_txn_url_from_token(token, proc_id=None):
    '''Returns the DragonPay payment URL given a token.'''

    d = {'tokenid': token}
    if proc_id:
        d['procid'] = proc_id

    return dp_settings.DRAGONPAY_PAY_URL + '?' + urllib.urlencode(d)


def get_txn_token_url(amount, description, email, proc_id=None, **params):
    '''Creates a DragonPay transaction and returns the Payment Switch URL.'''

    token = get_txn_token(amount, description, email, **params)

    if token:
        return get_txn_url_from_token(token[1], proc_id)


def get_txn_token(amount, description, email, txn_id=None, **params):
    '''Requests for a new DragonPay transaction and returns its txn_id and token.
    If not txn_id is passed, this method will generate one.

    return (tuple) - (txn_id, token)'''

    logger.debug(
        'get_txn_token %s %s %s %s', email, amount, description, params)

    txn_id = txn_id or generate_txn_id()
    context = {
        'txn_id': txn_id, 'amount': amount, 'email': email,
        'description': description}

    logger.debug('params %s', params)
    # include the params in the context
    for key, value in params.iteritems():
        if dp_settings.DRAGONPAY_ENCRYPT_PARAMS:
            # we cannot have a value of more than 47 chars since the
            # equivalent encrypted value will be more than 80 chars
            if len(value) > 47:
                raise ParamTooLong('Param %s when encrypted is > 80 chars')

            # Encrypt the params to obfuscate the payload
            logger.debug('Encrypting %s', value)
            value = encrypt_data(value)

        else:
            if len(value) > 80:
                raise ParamTooLong('Param %s length is > 80 chars')

        context[key] = value

    logger.debug('get_txn_token payload: %s', context)
    token = _dragonpay_get_wrapper('GetTxnToken', context=context)

    context['token'] = token
    context.update(params)      # include the raw params back to context
    DragonpayTransaction.create_from_dict(context)

    # check if the response token is an error code
    if len(token) < 4:
        msg = '[%s] %s' % (token, DRAGONPAY_ERROR_CODES[token])
        logger.error(msg)
        raise DragonpayException(msg)

    logger.debug('[%s] token %s for %s PhP %s', txn_id, token, email, amount)

    return txn_id, token


def get_txn_status(txn_id):
    '''Fetches the transaction status given a transaction id.'''

    context = {'txn_id': txn_id}
    txn_status = _dragonpay_get_wrapper('GetTxnStatus', 'webmethod', context)

    logger.debug(
        '[%s] txn status %s', txn_id, DRAGONPAY_STATUS_CODES[txn_status])

    return txn_status


def cancel_transaction(txn_id):
    '''Cancels the transaction given a transaction id. Returns True if the
    cancellation succeeds.'''

    context = {'txn_id': txn_id}
    status = _dragonpay_get_wrapper('CancelTransaction', context=context)

    if status == '0':
        logger.debug('[%s] Txn cancellation success', txn_id)
        return True

    else:
        logger.debug('[%s] Txn cancellation failed: %s', txn_id, status)


def get_txn_ref_no(txn_id):
    '''Fetches the reference number of a transaction.'''

    context = {'txn_id': txn_id}

    refno = _dragonpay_get_wrapper('GetTxnRefNo', 'webmethod', context)
    logger.debug('[%s] reference no: %s', txn_id, refno)
    return refno


def get_available_processors(amount):
    context = {'web_method': 'GetAvailableProcessors', 'amount': amount}
    context.update(CONTEXT)

    return _dragonpay_get_wrapper(
        'GetAvailableProcessors', 'GetAvailableProcessors',
        context=context)


def get_email_instructions(refno):
    response = requests.get(
        dp_settings.DRAGONPAY_BASE_URL + 'Bank/GetEmailInstruction.aspx',
        params={'refno': refno, 'format': 'json'})

    if response.status_code == 200:
        return json.loads(response.content)

    else:
        logger.error(
            'Error in getting email instructions: %s %s',
            response.status_code, response.content)


# PAYOUT RELATED SOAP METHODS
def _get_payout_data(webmethod, xml_name=None):
    '''Helper function for fetching data related to Payout.'''

    xmltree = _dragonpay_soap_wrapper(
        webmethod, xml_name=xml_name or 'GetPayoutData', payout=True)

    xmltree = xmltree.find(
        './/{http://api.dragonpay.ph/}%(webmethod)sResponse/'
        '{http://api.dragonpay.ph/}%(webmethod)sResult' % {
            'webmethod': webmethod}
    )
    data = []

    # convert the xmltree to dict
    for result in xmltree:
        subdata = {}
        for detail in result:
            subdata[detail.tag[detail.tag.index('}') + 1:]] = detail.text

        data.append(subdata)

    return data


def get_countries():
    '''Fetches data for the GetCountries Payout WebMethod.'''
    return _get_payout_data('GetCountries')


def get_processors():
    '''Fetches data for the GetProcessors Payout WebMethod.'''
    return _get_payout_data('GetProcessors')


def get_payout_txn_status(txn_id):
    '''Fetches the status of a payout transaction.'''
    context = {'txn_id': txn_id}

    txn_status = _dragonpay_get_wrapper(
        'GetTxnStatus', xml_name='GetPayoutTxnStatus',
        context=context, payout=True)

    logger.debug(
        '[%s] txn status %s',
        txn_id, DRAGONPAY_STATUS_CODES[txn_status])

    return txn_status


def modify_payout_channel():
    return _dragonpay_get_wrapper('ModifyPayoutChannel', payout=True)


def register_payout_user(user_details):
    '''Register a user for payout. The registered user can be given a payout
    using the request_payout method using his registered user_id.

    user_details (dict) - the user details of the user.
        see payout_context_keys for the list of fields that are required.'''

    payout_context_keys = {
        'address1', 'address2', 'birthdate', 'city', 'country', 'email',
        'first_name', 'last_name', 'middle_name', 'mobile', 'state', 'zip'}
    # Check that the given context contains the required fields
    if not set(user_details.keys()) == payout_context_keys:
        logger.debug(
            'Keys [%s] are missing from the RegisterPayoutUser context',
            ', '.join(set(user_details.keys()) - payout_context_keys))

        raise Exception('RegisterPayoutUser context invalid contents')

    return _dragonpay_get_wrapper(
        'RegisterPayoutUser', context=user_details, payout=True)


def request_multiple_payouts(payout_details):
    '''Requests for multiple payouts. This method and API only works for
    registered payout users.

    payout_details should contain the keys:
        txn_id, user_id, amount, currency, description'''

    if not isinstance(payout_details, list):
        raise Exception('payout_details must be a list')

    DragonpayPayout.create_from_dict(payout_details)

    rmp = 'RequestMultiplePayouts'
    return _get_payout_data(rmp, rmp)


def request_payout(txn_id, user_id, amount, description, currency=None):
    '''Request a payout to a registered user.'''

    context = {
        'txn_id': txn_id, 'user_id': user_id, 'amount': amount,
        'description': description, 'currency': currency}

    response_code = _dragonpay_soap_wrapper(
        'RequestPayout', context=context, payout=True)

    if response_code == '0':
        # save the dragonpay payout transaction to the database
        DragonpayPayout.create_from_dict(context)
    else:
        logger.error(
            '[%s] %s', response_code,
            DRAGONPAY_PAYOUT_ERROR_CODES[response_code])

    return response_code


def request_payout_ex(
        user_name, amount, description, proc_id,
        proc_detail, email, mobile, currency=None):
    '''Request for a one-time payout.

    user_name - the name of the individual that will receive the payout.
    amount - the amount to be given as payout.
    description - a short description for this transaction.
    proc_id - the processor id; see list of processors via get_processors
        method.
    proc_detail - the processor detail.
    email - the email of the individual that will receive the payout.
    mobile - the mobile number of the individual.
    currency - the currency to be used, defaults to PHP when None.

    Note: Payout transaction fees are not subtracted to the amount but
        will be shouldered by the merchant. So if we send amount=500,
        with a processor whose fee is PhP 15, PhP 515 will be deducted
        from our DragonPay account.'''

    txn_id = generate_txn_id()
    context = {
        'txn_id': txn_id,
        'user_name': user_name,
        'amount': amount,
        'currency': currency,
        'description': description,
        'processor_id': proc_id,
        'processor_detail': proc_detail,
        'timestamp': datetime.now(),
        'email': email,
        'mobile': mobile,
    }

    response_code = _dragonpay_get_wrapper(
        'RequestPayoutEx', context=context, payout=True)

    if response_code == '0':
        # save the dragonpay payout transaction to the database
        DragonpayPayout.create_from_dict(context)
    else:
        try:
            logger.error(
                '[%s] %s', response_code,
                DRAGONPAY_PAYOUT_ERROR_CODES[response_code])
        except KeyError:
            # Error is not in listed keys
            logger.error(
                'Error code [%s] not in DRAGONPAY_PAYOUT_ERROR_CODES',
                response_code)

    return response_code, txn_id
