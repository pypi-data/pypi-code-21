import contextlib
import requests
from bs4 import BeautifulSoup
from .login import LoginFlow


USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/57.0'


class RogersBankClient():
    def __init__(self, secret_provider, session=None):
        if session is None:
            session = requests.Session()
            session.headers.update({
                'User-Agent': USER_AGENT,
                'Upgrade-Insecure-Requests': '1',
                'Accept-Language': 'en-us',
                'Accept': 'text/html',
            })
        self._session = session
        self._login = LoginFlow(secret_provider, self._session)

    @contextlib.contextmanager
    def login(self):
        self._login.start()
        try:
            yield
        except Exception:
            raise
        finally:
            self._login.end()

    @property
    def recent_activities(self):
        response = self._session.get('https://rbaccess.rogersbank.com/Rogers_Consumer/RecentActivity.do')
        bs = BeautifulSoup(response.text, 'html.parser')
        table = bs.find('table', id='sortTable')
        recent_activities = []
        trs = table.find_all('tr')
        return [{
            'date': tr.find('td', class_='date').text.strip(),
            'description': list(tr.find('td', class_='description').children)[0].strip(),
            'amount': tr.find('td', class_='amount').text.strip(),
        } for tr in trs[1:]]
