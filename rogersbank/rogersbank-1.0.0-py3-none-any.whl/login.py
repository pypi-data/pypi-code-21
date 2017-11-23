from bs4 import BeautifulSoup
import logging


logger = logging.getLogger(__name__)


class LoginFlow(object):
    def __init__(self, secret_provider, session):
        self._secret_provider = secret_provider
        self._session = session

    def end(self):
        logger.info('Logging out...')
        response = self._session.get('https://rbaccess.rogersbank.com/Rogers_Consumer/Logoff.do')
        assert 'signed off' in response.text.lower()

    def start(self):
        logger.info('Initiating RogersBank logging flow')
        self._session.get('https://rbaccess.rogersbank.com/Rogers_Consumer/Login.do')
        username = self._secret_provider.get_username()
        password = self._secret_provider.get_password()
        response = self._session.post('https://rbaccess.rogersbank.com/Rogers_Consumer/ProcessLogin.do',
                                      data={
                                          'MFP': '{}',
                                          'IpAddress': '',
                                          'CallerID': '',
                                          'DeviceID': '',
                                          'username': username,
                                          'password': password,
                                      })
        response = self._answer_security_challenge(response, next='Next')
        response = self._answer_security_challenge(response, next='SIGN IN')

    def _answer_security_challenge(self, response, next):
        bs = BeautifulSoup(response.text, 'html.parser')
        challenge = bs.find('label', attrs={'for': 'hintanswer'}).text.strip()
        logging.info('Security Challenge: {}'.format(challenge))
        ctoken = bs.find('input', attrs={'name': 'cToken'}).attrs['value']
        taglibtoken = bs.find('input', attrs={'name': 'org.apache.struts.taglib.html.TOKEN'}).attrs['value']
        answer = self._secret_provider.get_security_challenge_answer(challenge)
        response = self._session.post('https://rbaccess.rogersbank.com/Rogers_Consumer/SecondaryAuthMultiple.do',
                                      data={
                                          'cToken': ctoken,
                                          'org.apache.struts.taglib.html.TOKEN': taglibtoken,
                                          'registerTrustedComputer': 'No',
                                          'submitNext': next,
                                          'hintanswer': answer,
                                      })
        assert 'wrong security answer' not in response.text.lower()
        return response
