import io
import os
import logging
import argparse
import urllib2
import collections
import sha
from datetime import datetime
from decimal import Decimal
from bs4 import BeautifulSoup
from urlparse import urlparse
from notify import notify
from config import keyword, main_dir

logger = logging.getLogger(__name__)

vatan_host = 'http://www.vatanbilgisayar.com/'

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}

def fetch_price(uri):
    request = urllib2.Request(url=vatan_host + uri, headers=headers)
    response = urllib2.urlopen(request)
    soup = BeautifulSoup(response.read(), 'html.parser')

    price_elem = soup.find('td', class_=keyword).contents[0]
    amount, currency = price_elem.split()
    amount = amount.replace(',', '')
    desc = unicode(soup.h1.contents[0])

    logger.debug('amount=%s, currency=%s, desc=%s', amount, currency, desc)
    item = ItemSnapshot(desc, amount, currency)
    return item
    # print soup.find('span', class_='urunDetay_satisFiyat').contents[0]
    # print soup.find('span', class_='urunDetay_satisFiyat')
    # \.contents[1].contents[0]


def read_item(path):
    """ Reads url from item file path given.
    <uri>:<last-amount>:<currency>
    <date>::<last-amount>:<currency>
    """
    item = None
    with io.open(main_dir + path, 'rt', encoding='UTF-8', newline=None) as f:
        s = f.readline().split(':')
        print s
        uri, amount, currency = s
        item = Item(uri, Decimal(amount), currency)
    return item


def read_items():
    return [read_item(path) for path in os.listdir(main_dir) if path != '.mailpass']


def make_item_path(uri):
    return sha.new(uri).hexdigest()


def persist(path, snapshot):
    with io.open(main_dir + path, 'at', encoding='UTF-8', newline=None) as f:
        ser = ':'.join((datetime.strftime(snapshot.datetime, "%Y-%m-%d %H:%M"),
                        str(snapshot.amount).encode('UTF-8'),
                        snapshot.currency))
        f.write(ser + os.linesep)


class ItemSnapshot(object):
    """Represents a snapshot of the price of self.name at self.datetime
    Attributes:
        name (str): Description of `attr1`.
        amount (Decimal) attr2 (:obj:`int`, optional): Description of `attr2`.
        currency (str)
        datetime (datetime)
    """
    def __init__(self, name, amount, currency, created=None):
        self.name = name
        self.amount = Decimal(amount)
        self.currency = currency
        self.datetime = datetime if created else datetime.now()

    def __str__(self):
        return 'ItemSnapshot[datetime=%s, amount=%s%s]' \
               % (self.datetime, self.amount, self.currency)


class Item(object):
    def __init__(self, uri, amount, currency):
        self.uri = uri
        self.amount = Decimal(amount)
        self.currency = currency

    def __str__(self):
        return 'Item[uri=%s, amount=%s%s]' \
                % (self.uri, self.amount, self.currency)


class Container(object):
    def __init__(self, name):
        self.name = name
        self.prices = collections.OrderedDict()

    def add_item(self, item):
        self.prices[item.datetime] = item


def read_history():
    def get_file_name():
        return os.environ["HOME"] + '/.item_prices'

    c = Container('abc')

    with io.open(get_file_name(), 'rt', encoding='UTF-8', newline=None) as f:
        for ln, line in enumerate(f, 1):
            name, amount, currency, date = line.rstrip(os.linesep).split(';')
            logger.debug('ln#%s: name=%s, amount=%s, currency=%s, date="%s"',
                         ln, name, amount, currency, date)
            item = ItemSnapshot(name, amount, currency,
                                datetime.strptime(date, "%Y-%m-%d %H:%M"))
            c.add_item(item)
    print c.prices


def register(url):
    if not create_dir_if_not_exists():
        notify.store_user_email()
        os.system("echo \"* * * * * python -m vatan pull\" | crontab -")

    if url.index(vatan_host):
        raise ValueError('Bad url', url)

    uri = url[len(vatan_host):]
    snapshot = fetch_price(uri)
    item = Item(uri, snapshot.amount, snapshot.currency)
    full_path = main_dir + make_item_path(uri)
    with io.open(full_path, 'wt', encoding='UTF-8', newline=None) as f:
        ser = ':'.join((item.uri,
                        str(item.amount).encode('UTF-8'),
                        item.currency))
        f.write(ser + os.linesep)
    

def parse_args():
    """
    Usage:
    vatan.py pull
    vatan.py reg <url>
    """

    def valid_url(url):
        result = urlparse(url)
        host = result.scheme + '://' + result.netloc + '/'
        if host != vatan_host:
            raise argparse.ArgumentTypeError('Bad url: %s' % url)
        return url

    parser = argparse.ArgumentParser()

    parser.add_argument('-v', '--verbose', help='verbose output',
                        action='store_const', dest='loglevel',
                        const=logging.DEBUG, default=logging.INFO)

    subparsers = parser.add_subparsers(dest='command')

    pull_parser = subparsers.add_parser('pull')

    reg_parser = subparsers.add_parser('reg')
    reg_parser.add_argument('url', type=valid_url)
    reg_parser.add_argument('--delta', type=int, default=10,
                            help='price delta')

    return parser.parse_args()


def validate_url(url):
    result = urlparse(url)
    host = result.scheme + '://' + result.netloc + '/'
    if host != vatan_host:
        raise argparse.ArgumentTypeError('Bad url: %s' % url)
    return url


def ping():
    return '%s: pong!' % __name__


def create_dir_if_not_exists():
    exists = os.path.exists(main_dir)
    if not exists:
        os.mkdir(main_dir, 0774)
    return exists


def main():
    args = parse_args()

    if args.command == 'reg':
        register(args.url)
    elif args.command == 'pull':
        for i in read_items():
            snapshot = fetch_price(i.uri)
            persist(make_item_path(i.uri), snapshot)
            if snapshot.amount != i.amount:
                notify.send_mail(i, snapshot)
    elif args.command == 'read':
        pass
    else:
        pass

#        try:
#            item = fetch_price(url)
#            if abs(ref_amount - item.amount) >= delta:
#                print 'price change event'
#            persist(item)
#        except urllib2.HTTPError as e:
#            logger.error('HttpError code=%s, url="%s":%s',
#                         e.code, url, e, exc_info=True)


if __name__ == '__main__':
    main()
