import codecs
import re


class FileReciver:

    def __init__(self, quotation_file=None, deals_file=None):
        self.quotation_file = quotation_file
        self.deals_file = deals_file

    def iter_quotation(self, stock_filter='sh6.*|sz00.*|sz30.*'):
        if self.quotation_file is None:
            return
        f = codecs.open(self.quotation_file, 'r',
                        'utf-8', buffering=1024 * 1024)
        filter_regex = re.compile(stock_filter)
        for line in f:
            symbol = line[:line.find(',')]
            if filter_regex.search(symbol) is not None:
                yield line.strip()

    def iter_deals(self, stock_filter='sh6.*|sz00.*|sz30.*'):
        if self.deals_file is None:
            return
        f = codecs.open(self.deals_file, 'r', 'utf-8', buffering=1024 * 1024)
        filter_regex = re.compile(stock_filter)
        for line in f:
            symbol = line[:line.find('=')]
            if filter_regex.search(symbol) is not None:
                yield line.strip()

    def iter_multi(self, stock_filter='sh6.*|sz00.*|sz30.*', listen='quotation'):
        """
        获取多种行情
        Parameters
        --------
        stock_filter:匹配股票代码
        listen:接收指定行情，可为quotation,deals,orders,多种请用|间隔或者传入iterable
        """
        self.listen = listen.split('|') if isinstance(listen, str) else listen
        if 'quotation' in self.listen:
            for q in self.iter_quotation(stock_filter):
                yield ('quotation', q)
        if 'deals' in self.listen:
            for q in self.iter_deals(stock_filter):
                yield ('deals', q)
