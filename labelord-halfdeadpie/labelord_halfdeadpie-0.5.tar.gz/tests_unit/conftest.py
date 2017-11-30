import configparser
import os

import requests
from betamax.fixtures.pytest import betamax_session
from flexmock import flexmock

from labelord.cli_support import Label

ABS_PATH = os.path.abspath(os.path.dirname(__file__))
FIXTURES_PATH = ABS_PATH + '/fixtures/'
CASSETTES_PATH = FIXTURES_PATH + '/cassettes/'
CONFIGS_PATH = FIXTURES_PATH + '/configs/'
FAKE_TOKEN = 'JustSomeRandomTokenForTesting'
CASSETTES_PATH = 'tests_unit/fixtures/cassettes'
DATA_PATH = FIXTURES_PATH + '/data'


"""Create fake context with fake session"""
FAKE_CTX = flexmock(obj = { 'session':  betamax_session,
                            'config': 'config.cfg',
                            'token': 'bc668397dddcca318c14cbb171b2c623903af4f4',
                            'updated': [],
                            'errors': [] },
                    resilient_parsing = False,
                    exit=lambda: None)

"""Create fake request for web_support testing"""
FAKE_REQUEST = flexmock\
    (headers = {
    'X-Hub-Signature': 'sha1=b7a7bacc401abde76ef575b2f3f436ae28aad8ec',
    'X-GitHub-Event': 'ping',
    'X-Github-Delivery': '64603d10-a3bb-11e7-82bc-0764f2d1a900',
    'X-Request-Id': 'e118e5e1-6763-4854-8b19-595c27b00135'
    },
    data = 'justSomeRandomData'.encode('utf-8')
    )




REPOS = ['HalfDeadPie/Games',
        'HalfDeadPie/LoRa-FIIT',
        'HalfDeadPie/MusicAppForEma',
        'HalfDeadPie/Software-bridge',
        'HalfDeadPie/Software-router',
        '']

LABELS = ['#e99695 SkuskaSkuskaSkuska',
            '#4767ad Tristo',
            '']


RUN_DRY = [
'[ADD][DRY] HalfDeadPie/Software-router; Bug; 1af480',
'[UPD][DRY] HalfDeadPie/Software-router; LOL; 38c1e0',
'[ADD][DRY] HalfDeadPie/Software-router; New; 64ef99',
'[ADD][DRY] HalfDeadPie/Software-router; Shock; 8aabd8',
'[ADD][DRY] HalfDeadPie/Software-router; Weird; a0e56b',
'[ADD][DRY] HalfDeadPie/Software-bridge; Bug; 1af480',
'[ADD][DRY] HalfDeadPie/Software-bridge; LOL; 38c1e0',
'[ADD][DRY] HalfDeadPie/Software-bridge; New; 64ef99',
'[ADD][DRY] HalfDeadPie/Software-bridge; Shock; 8aabd8',
'[ADD][DRY] HalfDeadPie/Software-bridge; Weird; a0e56b',
'[ADD][DRY] HalfDeadPie/LoRa-FIIT; Bug; 1af480',
'[ADD][DRY] HalfDeadPie/LoRa-FIIT; LOL; 38c1e0',
'[ADD][DRY] HalfDeadPie/LoRa-FIIT; New; 64ef99',
'[ADD][DRY] HalfDeadPie/LoRa-FIIT; Shock; 8aabd8',
'[ADD][DRY] HalfDeadPie/LoRa-FIIT; Weird; a0e56b',
'[SUMMARY] 3 repo(s) updated successfully',
''
]

TARGET_REPOS = [
'HalfDeadPie/Software-router',
'HalfDeadPie/Software-bridge',
'HalfDeadPie/LoRa-FIIT',
]


INFO = 'labelord application is master-to-master application for label replication using webhook for GitHub<br>HalfDeadPie/Software-router https://github.com/HalfDeadPie/Software-router<br>HalfDeadPie/Software-bridge https://github.com/HalfDeadPie/Software-bridge<br>HalfDeadPie/LoRa-FIIT https://github.com/HalfDeadPie/LoRa-FIIT<br>'

HEADER_CREATED = headers={
                              'Content-Type': 'application/json',
                              'User-Agent': 'GitHub-Hookshot/e20df6f',
                              'X-Hub-Signature': 'sha1=1c62273cd11291f5b621cce75b21deab53c03a41',
                              'X-GitHub-Event': 'label',
                              'X-Github-Delivery': '9f55b9b0-cc68-11e7-8584-56dc6e8e94ec',
                              'X-Request-Id': 'bfa3c2d7-34d3-459f-af1f-7bbaf7e181b7'
                          }

HEADER_EDITED = headers={
                              'Content-Type': 'application/json',
                              'User-Agent': 'GitHub-Hookshot/e20df6f',
                              'X-Hub-Signature': 'sha1=3ba6ba9f2831f8a5cf09012db860b0f900a9ea2d',
                              'X-GitHub-Event': 'label',
                              'X-Github-Delivery': 'b8ead090-cc86-11e7-8363-65111c2702e2',
                              'X-Request-Id': 'ba0bd2ec-25cd-45a7-84dd-281da697cf81'
                          }

HEADER_DELETED = headers={
                              'Content-Type': 'application/json',
                              'User-Agent': 'GitHub-Hookshot/e20df6f',
                              'X-Hub-Signature': 'sha1=f366e800720cb1300ddd8e5e2c5c147374f57357',
                              'X-GitHub-Event': 'label',
                              'X-Github-Delivery': '6da11c06-cc87-11e7-866e-325d152a9020',
                              'X-Request-Id': '78640733-e1b8-4123-98b5-d6843a566a40'
                          }


def token_real():
    parser = configparser.ConfigParser()
    parser.optionxform = str
    parser.read(CONFIGS_PATH + 'config.cfg')
    if (parser.has_section('github')):
        return parser['github']['token']

def secret_real():
    parser = configparser.ConfigParser()
    parser.optionxform = str
    parser.read(CONFIGS_PATH + 'config.cfg')
    if (parser.has_section('github')):
        return parser['github']['webhook_secret']

def labels_basic():
    parser = configparser.ConfigParser()
    parser.optionxform = str
    parser.read(CONFIGS_PATH + 'config_basic.cfg')
    basic_template = []
    if (parser.has_section('labels')):
        for (each_key, each_val) in parser.items('labels'):
            lb = Label(each_key, each_val)
            basic_template.append(lb)
    return basic_template

class invoker():
    @staticmethod
    def configs():
        """Function returns the path to config files"""
        return CONFIGS_PATH

    @staticmethod
    def cassette():
        """Return the cassettes path"""
        return CASSETTES_PATH

    @staticmethod
    def real_config():
        """Return name of real config"""
        return 'config.cfg'

    @staticmethod
    def basic_config():
        return 'config_basic.cfg'

    @staticmethod
    def bad_config():
        return 'config_bad.cfg'

    @staticmethod
    def repos():
        """Return the array of my repos"""
        return REPOS

    @staticmethod
    def token():
        """Function returns example of fake token"""
        return FAKE_TOKEN


    @staticmethod
    def ctx():
        return FAKE_CTX

    @staticmethod
    def labels():
        return labels_basic()

    @staticmethod
    def token_true():
        return token_real()

    @staticmethod
    def secret_true():
        return secret_real()

    @staticmethod
    def repo_labels():
        # return labels from repo HalfDeadPie/LoRa-FIIT
        return LABELS

    @staticmethod
    def run_dry():
        # return output from run dry
        return RUN_DRY

    @staticmethod
    def target_repos():
        return TARGET_REPOS

    @staticmethod
    def request():
        return FAKE_REQUEST

    @staticmethod
    def info():
        return INFO

    @staticmethod
    def load_data(name):
        with open(DATA_PATH + '/' + name + '.json') as f:
            return f.read()

    @staticmethod
    def header_created():
        return HEADER_CREATED

    @staticmethod
    def header_edited():
        return HEADER_EDITED

    @staticmethod
    def header_deleted():
        return HEADER_DELETED