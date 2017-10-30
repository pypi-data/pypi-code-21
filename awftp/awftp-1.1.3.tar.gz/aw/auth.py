# The MIT License (MIT)
#
# Copyright (c) 2016-2017 Thorsten Simons (sw@snomis.de)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import requests
import logging
import click
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from aw.exceptions import SamlAuthError
from aw.init import minapi_saml


def samlauth(session=None, anywhere=None, idp=None, user=None, password=None,
             forceapi=None):
    '''
    Authenticate against a SAML IDP.
    :return:
    '''
    logger = logging.getLogger(__name__)

    # check for the requested FSS API
    if forceapi and forceapi < minapi_saml:
        raise SamlAuthError('forced API {} is too low - need at least {} for '
                            'SAML auth'.format(forceapi, minapi_saml))
    else:
        api = minapi_saml if not forceapi or not forceapi > minapi_saml else forceapi
    logger.debug('api used is {}'.format(api))

    with click.progressbar(length=4, show_eta=False, show_pos=True,
                           label="Performing SAML authentication") as bar:

        logger.debug('IDP = {}'.format(idp))
        # set default headers required by HCP Anywhere FSS-API and SAML auth
        session.headers.update({'Accept': 'application/json',
                                'Content-Type': 'application/json',
                                'X-HCPAW-FSS-API-VERSION': api})
        logger.debug('==> listing available authentication providers:')
        try:
            r = session.post(anywhere + '/fss/public/provider/list')
        except Exception as e:
            raise SamlAuthError('LIST IDP error - {}'.format(e))
        else:
            if r.status_code != 200:
                raise SamlAuthError('LIST IDP error ({} - {})'
                                    .format(r.status_code, r.reason))
        logger.debug(' --> headers:')
        logger.debug('{}'.format(r.headers))
        logger.debug('{:16}   {:20}   {}'.format('type', 'name', 'id'))
        logger.debug('{}'.format(79 * '-'))
        api = forceapi or sorted(
            r.headers['X-HCPAW-SUPPORTED-FSS-API-VERSIONS'].split(','),
            reverse=True)[0]
        session.headers.update({'X-HCPAW-FSS-API-VERSION': api})
        auth = None
        for _idp in r.json()['providers']:
            logger.debug('{:16}   {:20}   {}'.format(_idp['type'],
                                                     _idp['name'],
                                                     _idp['id']))
            if _idp['name'] == idp:
                auth = {'id': _idp['id'],
                        'clientType': 'PORTAL'
                        }
        if not auth:
            raise SamlAuthError('SAML IDP {} unknown by {}'
                                .format(idp, anywhere))
        bar.update(1)

        logger.debug('==> now calling /fss/public/saml/redirect:')
        try:
            logger.debug('request body:')
            logger.debug(auth)
            r = session.post(anywhere+'/fss/public/saml/redirect',
                             json=auth, allow_redirects=True)
        except requests.exceptions.ConnectionError as e:
            raise SamlAuthError('Connection to {} failed - {}'
                                .format(anywhere, e))
        else:
            logger.debug('--> call returned {}'.format(r.status_code))
            logger.debug('--> returned headers:')
            logger.debug(r.headers)
            logger.debug('--> returned body:')
            logger.debug(r.text)
            logger.debug('==> DONE calling /fss/public/saml/redirect <==')
            if r.status_code != 200:
                raise SamlAuthError('initial SAML authentication failed '
                                    '({} {}).'
                                    .format(r.status_code, r.reason))
        logger.debug('==> now preparing response to the IDP:')
        (_host, _action, _form) = getform(r, user, password)
        logger.debug('IDP = {}'.format(_host))
        logger.debug('form action = {}'.format(_action))
        logger.debug('form fields and values:')
        logger.debug(_form)
        bar.update(1)

        logger.debug('==> now calling the IDP with the form')
        try:
            _y = requests.request('POST', _host + _action,
                                  data=_form, verify=False,
                                  allow_redirects=False,
                                  headers={'Accept': 'application/xml',
                                           'Content-Type': 'application/x-www-form-urlencoded'}
                                  )
        except Exception as e:
            raise SamlAuthError('Connection to the SAML IDP failed - {}'
                                .format(e))
        else:
            if _y.status_code != 200:
                raise SamlAuthError('calling the SAML IDP failed ({} - {})'
                                    .format(_y.status_code,
                                            _y.reason))
        logger.debug('--> called {}{}...'.format(_host, _action[:30]))
        logger.debug('--> call returned {}'.format(_y.status_code))
        logger.debug('--> returned headers:')
        logger.debug(_y.headers)
        logger.debug('--> returned body:')
        logger.debug(_y.text)
        logger.debug('==> DONE calling IDP <==')
        bar.update(1)

        logger.debug('==> now preparing call to .../mobile/saml/saml/SSO:')
        (_host, _action, _form) = getform(_y, user, password)
        logger.debug('anywhere = {}'.format(_host))
        logger.debug('form action = {}'.format(_action))
        logger.debug('form fields and values:')
        logger.debug('{}'.format(_form))

        logger.debug('==> now calling .../mobile/saml/saml/SSO with the form')
        try:
            _y = session.post(_host + _action,
                              data=_form, verify=False,
                              allow_redirects=True,
                              headers={'Accept': 'application/xml',
                                       'Content-Type': 'application/x-www-form-urlencoded'},
                              )
        except Exception as e:
            raise SamlAuthError('calling HCP Anywhere SSO endpoint '
                                'failed - {}'.format(e))
        else:
            if _y.status_code != 200:
                raise SamlAuthError('calling HCP Anywhere SSO '
                                    'endpoint failed ({} - {})'
                                    .format(_y.status_code,
                                            _y.reason))

        logger.debug('--> called {}{}...'.format(_host, _action[:50]))
        logger.debug('--> call returned {}'.format(_y.status_code))
        logger.debug('--> returned headers:')
        logger.debug(_y.headers)
        logger.debug('--> returned body:')
        logger.debug(_y.text)
        logger.debug('--> known cookies:')
        logger.debug(session.cookies)
        logger.debug('...and the same as dict:')
        _rc = requests.utils.dict_from_cookiejar(session.cookies)
        logger.debug(_rc)
        logger.debug('==> DONE calling .../mobile/saml/saml/SSO <==')
        # see if login failed
        if not 'XSRF-TOKEN' in _rc.keys() or not _rc['XSRF-TOKEN']:
            raise SamlAuthError('login failed - check username and password')
        bar.update(1)

        session.headers.update({'X-XSRF-TOKEN': _rc['XSRF-TOKEN']})
        return api

def getform(r, user, password):
    """
    Finds a form in an html document and returns its fields as a dict.

    :param r:           the requests.response object
    :param user:        user name
    :param password:    password
    :return:            the host to call with the form,
                        the action to perform on that host,
                        a dict with the form values
    """
    logger = logging.getLogger(__name__)
    soup = BeautifulSoup(r.text, 'html.parser')
    _action = soup.form['action']
    if not _action.startswith('http'):
        # get the host that sent the reply (the IDP)
        _ = urlparse(r.url)
        _host = '://'.join([_.scheme, _.netloc])
    else:
        _host = ''
    logger.debug('{}, {}'.format(_host, _action))

    _form = {}
    for inp in soup.form.find_all('input'):
        try:
            if 'user' in inp.get('name').lower():
                _form[inp.get('name')] = user
            elif 'password' in inp.get('name').lower():
                _form[inp.get('name')] = password
            else:
                _form[inp.get('name')] = inp.get('value')
        except AttributeError:
            _form[inp.get('type')] = inp.get('value')

    return(_host, _action, _form)
