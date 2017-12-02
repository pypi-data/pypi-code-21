import contextlib
import requests
from bs4 import BeautifulSoup
from .login import LoginFlow


USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/57.0'


def extract_csrf_tokens(bs):
    ctoken = bs.find('input', attrs={'name': 'cToken'}).attrs['value']
    taglibtoken = bs.find('input', attrs={'name': 'org.apache.struts.taglib.html.TOKEN'}).attrs['value']
    return {
        'cToken': ctoken,
        'org.apache.struts.taglib.html.TOKEN': taglibtoken,
    }


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
    def account_overview(self):
        response = self._session.get('https://rbaccess.rogersbank.com/Rogers_Consumer/RecentActivity.do')
        bs = BeautifulSoup(response.text, 'html.parser')
        trs = bs.find('div', class_='sidebar').find('table').find_all('tr')
        assert len(trs) == 3
        last_statement = {
            'balance': trs[0].find('td', class_='value').text.strip(),
            'minimum_payment': trs[1].find('td', class_='value').text.strip(),
            'due_date': trs[1].find('td', class_='value').text.strip(),
        }

        balance = list(bs.find_all('td', class_='value')[1].children)[0].text.strip()  # XXX: thanks rogersbank for can't write well-formed HTML
        return {
            'current_balance': balance,
            'last_statement': last_statement,
        }

    @property
    def recent_activities(self):
        response = self._session.get('https://rbaccess.rogersbank.com/Rogers_Consumer/RecentActivity.do')
        bs = BeautifulSoup(response.text, 'html.parser')
        table = bs.find('table', id='sortTable')
        trs = table.find_all('tr')
        return [{
            'date': tr.find('td', class_='date').text.strip(),
            'description': list(tr.find('td', class_='description').children)[0].strip(),
            'amount': tr.find('td', class_='amount').text.strip(),
        } for tr in trs[1:]]

    @property
    def billing_cycles(self):
        response = self._session.get('https://rbaccess.rogersbank.com/Rogers_Consumer/TransHistory.do')
        bs = BeautifulSoup(response.text, 'html.parser')
        select = bs.find('select')
        options = select.find_all('option')

        return [{
            'name': option.text.strip(),
            'value': option.attrs['value']
        } for option in options]

    def download_statement(self, billing_cycle_value, filetype='ofx', base_filename='report', save=True):
        assert filetype in ('qif', 'csv', 'tsv', 'iif', 'ofx')
        response = self._session.get('https://rbaccess.rogersbank.com/Rogers_Consumer/TransHistory.do')
        bs = BeautifulSoup(response.text, 'html.parser')
        data = dict(extract_csrf_tokens(bs.find('form', {'name': 'transHistoryForm'})))
        data['cycleDate'] = billing_cycle_value

        response = self._session.post('https://rbaccess.rogersbank.com/Rogers_Consumer/TransHistory.do',
                                      data=data)
        bs = BeautifulSoup(response.text, 'html.parser')
        data = dict(extract_csrf_tokens(bs.find('form', {'name': 'downLoadTransactionForm'})))
        data['downloadType'] = filetype
        response = self._session.post('https://rbaccess.rogersbank.com/Rogers_Consumer/DownLoadTransaction.do',
                                      data=data)
        response.raise_for_status()
        if save:
            filename = '{}.{}'.format(base_filename, filetype)
            with open(filename, 'w') as f:
                f.write(response.text)
            return filename
        else:
            return response.text
