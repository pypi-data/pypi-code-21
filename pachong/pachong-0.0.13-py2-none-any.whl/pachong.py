#-*-coding:utf-8-*-
__author__ = 'cchen'

import csv
import json
import re
import time
from datetime import datetime, timedelta
from os import path

from bs4 import BeautifulSoup
from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util import Retry


class PaChong(object):
    MAX_RETRIES = 9
    STATUS_FORCELIST = [500]

    def __init__(self, session=None):
        self.session = self.set_session(session)
        self.session.default_timeout = 10

    def set_session(self, session=None):
        if session:
            return session
        session = Session()
        retries = Retry(total=self.MAX_RETRIES, status_forcelist=self.STATUS_FORCELIST)
        session.mount('https://', HTTPAdapter(max_retries=retries))
        session.default_timeout = 10
        session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 '
                                              '(KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36'})
        return session

    @staticmethod
    def write_list(obj, fp):
        with open(fp, 'a') as o:
            [o.write(item + '\n') for item in obj]

    @staticmethod
    def read_list(fp):
        if not path.exists(fp):
            return set()
        with open(fp, 'r') as i:
            return {line.strip() for line in i if line.strip()}

    @staticmethod
    def write_records(obj, fp, log=None, log_prefix=u''):
        count_write = 0
        with open(fp, 'a') as o:
            csvwriter = csv.writer(o, delimiter='\t')
            for item in obj:
                csvwriter.writerow(item)
                count_write += 1
        print log_prefix + u'写入{}个新{}'.format(count_write, log) if log or log_prefix else ''

    @staticmethod
    def read_records(fp, col_id=0):
        if not path.exists(fp):
            return set()
        with open(fp, 'r') as i:
            csvreader = csv.reader(i, delimiter='\t')
            if isinstance(col_id, tuple):
                return {'_'.join(row[ind] for ind in col_id)
                        for row in csvreader}
            else:
                return {row[col_id]
                        for row in csvreader if row[col_id]}

    @staticmethod
    def write_line(obj, fp):
        with open(fp, 'a') as o:
            o.write(obj + '\n')

    @staticmethod
    def utc_now():
        return (datetime.now() - datetime(1970, 1, 1)).total_seconds()

    @staticmethod
    def hibernate(minutes=0):
        now = datetime.now()
        this_time = datetime(year=now.year, month=now.month, day=now.day, hour=now.hour)
        next_time = this_time + timedelta(minutes=minutes)
        sleeptime = (next_time - now).total_seconds()
        sleeptime = sleeptime if sleeptime > 0 else sleeptime + minutes * 60
        print u' 任务完成时间{}, {}分钟后重启任务'.format(now.strftime('%Y-%m-%d %H:%M:%S'), int(sleeptime) / 60)
        time.sleep(sleeptime)

    def get_soup(self, url, **kwargs):
        html = self.session.get(url, **kwargs)
        soup = BeautifulSoup(html.content, 'lxml')
        return soup

    def get_json(self, url, **kwargs):
        html = self.session.get(url, **kwargs)
        data = json.loads(html.content)
        return data

    @staticmethod
    def parse_script(script, within=None):
        if within:
            if isinstance(within, (str, unicode)):
                within = re.compile(within)
            if isinstance(within, re._pattern_type):
                script = within.search(script)
                if script is None:
                    return dict()
                script = script.group(1)
        return json.loads(script)

    @staticmethod
    def json_has(data, attrs):
        for key, val in attrs.iteritems():
            if isinstance(val, re._pattern_type):
                if not val.search(data.get(key)):
                    return False
            elif isinstance(val, (str, unicode)):
                if data.get(key) != val:
                    return False
        return True

    @staticmethod
    def get_page_property(jscript, var_name):
        if var_name.startswith('$'):
            var_name = var_name[1:]
        for line in jscript.splitlines():
            line = re.sub('\\$|var |;$', '',line.strip())
            if re.compile(var_name).search(line):
                try:
                    exec line
                except:
                    pass
        return eval(var_name)
