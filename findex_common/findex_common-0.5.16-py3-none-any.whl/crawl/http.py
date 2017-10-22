import re
from bs4 import BeautifulSoup, Tag
import dateutil.parser

from humanfriendly import parse_size as human2bytes
from urllib.parse import unquote_plus


class HttpParse:
    def __init__(self):
        self.parser = None

        # suitable parsers for open HTTP directories
        self.parsers = {
            'apache': [
                self._parse1,
                self._parse2,
                self._parse3,
            ],
            'nginx': [
                self._parse3,
                self._parse2,
                self._parse1,
            ],
            'unknown': [
                self._parse4,
                self._parse1,
                self._parse2,
                self._parse3
            ]
        }

    def get_parser(self, response_headers, response_body):
        # sanitize response headers
        response_headers = {k.lower(): v for k, v in response_headers.items()}

        # check response type, should be HTML
        # @TODO: HTML check

        if 'server' in response_headers:
            if response_headers['server'].startswith('apache'):
                response_headers['server'] = 'apache'
            elif response_headers['server'].startswith('nginx'):
                response_headers['server'] = 'nginx'
            else:
                response_headers['server'] = 'unknown'
        else:
            response_headers['server'] = 'unknown'

        if response_headers['server'] in self.parsers:
            parsers = self.parsers[response_headers['server']]

            for parser in parsers:
                try:
                    data = parser(response_body)
                    if data:
                        self.parser = parser

                        return self.parser
                except Exception as ex:
                    pass

        # no suitable index parser found at this point, do some regex on <a> tags
        try:
            data = self._parse4(response_body)
            if data:
                self.parser = self._parse4

                return self.parser
        except:
            pass

    def _parse1(self, content):
        """
        Default apache 2.* index template

        :param content: HTML
        :return: directory contents
        """
        parent_root = ''
        soup = BeautifulSoup(content, "html.parser")

        for a in soup.findAll('a', href=True):
            if '../' in a.text.lower() or 'parent directory' in a.text.lower():
                parent_root = a.parent

        if not parent_root.name == 'td':
            return

        columns = []
        for th in soup.findAll('th'):
            ass = th.find('a', href=True)

            columns.append(None if not ass else ass.text.lower())

        data = []
        for item in parent_root.parent.parent.findAll('tr'):
            if not item.name == 'tr':
                continue

            if item.contents and item.contents[0].name == 'th':
                continue

            f = {
                'filename': None,
                'isdir': False,
                'size': 0,
                'modified': None
            }
            c = item.contents

            filename = c[1].text.lower().strip()
            if filename.startswith('parent directory') or filename.startswith('-'):
                continue

            fn = self._getNameUrlIsdir(c[1].contents[0].attrs['href'])
            if not fn:
                continue

            f['filename'], f['url'], f['isdir'] = fn

            if c[2].text.strip():
                try:
                    f['modified'] = dateutil.parser.parse(c[2].text.strip())
                except:
                    pass

            f['size'] = self._getBytes(c[3].text, f)

            data.append(f)
        return self._cleanData(data)

    def _parse2(self, content):
        """
        Weird Apache template, unknown version

        :param content:
        :return: directory contents
        """
        parent_root = ''
        soup = BeautifulSoup(content, "html.parser")

        for b in soup.findAll('a', href=True):
            if '../' in b.text.lower() or 'parent directory' in b.text.lower():
                parent_root = b.parent

        if not parent_root.name == 'li':
            return

        data = []
        for item in parent_root.parent.findAll('li')[1:]:
            f = {
                'filename': None,
                'isdir': False,
                'size': 0,
                'modified': None
            }

            a = item.find('a')
            if 'href' not in a.attrs:
                continue

            fn = self._getNameUrlIsdir(a.attrs['href'])
            if not fn:
                continue

            f['filename'], f['url'], f['isdir'] = fn

            data.append(f)
        return self._cleanData(data)

    def _parse3(self, content):
        """
        nginx template, tested on 1.2.1

        :param content: HTML
        :return: directory contents
        """
        soup = BeautifulSoup(content, "html.parser")

        container = soup.find('pre')
        if not container:
            return

        data = []
        for a in container.findAll('a', href=True):
            f = {
                'filename': None,
                'isdir': False,
                'size': 0,
                'modified': None
            }

            if not 'href' in a.attrs:
                continue

            if 'parent directory' in a.text.lower() or '../' in a.text:
                continue

            fn = self._getNameUrlIsdir(a.attrs['href'])
            if not fn:
                continue

            f['filename'], f['url'], f['isdir'] = fn

            def _parse(inp):
                modified, size = [z.strip() for z in inp.split('  ') if z and z.strip()]
                return dateutil.parser.parse(modified), self._getBytes(size, f)

            def _test1(c):
                return _parse(c[2])

            def _test2(c):
                for i in range(0, len(c)):
                    if isinstance(c[i], Tag):
                        if 'href' in c[i].attrs:
                            if c[i].attrs['href'] == a.attrs['href']:
                                return _parse(c[i+1])

            for test in [_test1, _test2]:
                try:
                    modified, size = test(a.parent.contents)
                    f['modified'] = modified
                    f['size'] = size
                except:
                    pass

            data.append(f)
        return self._cleanData(data)

    def _parse4(self, content):
        """
        fetches all links from a webpage and treats found items as directories or files

        :param content: HTML
        :return: directory contents
        """
        urls = re.findall(r'href=[\'"]?([^\'" >]+)', content)

        data = []
        for url in urls:
            f = {
                'filename': None,
                'isdir': False,
                'size': 0,
                'modified': None
            }

            fn = self._getNameUrlIsdir(url)
            if not fn:
                continue

            f['filename'], f['url'], f['isdir'] = fn

            data.append(f)
        return self._cleanData(data)

    @staticmethod
    def _cleanData(data):
        rtn = []
        filenames = []

        for item in data:
            if item["filename"] in ('.', '..', ''):
                continue
            if item['filename'] not in filenames:
                rtn.append(item)
                filenames.append(item['filename'])
        return rtn

    def _getNameUrlIsdir(self, inp):
        inp = inp.strip()

        if not inp.startswith('?C=') and not inp.startswith('..'):
            isdir = False

            url = re.sub('%[a-f0-9]{2}', lambda m: m.group(0).upper(), inp)

            if inp.endswith('/'):
                isdir = True
                inp = inp[:-1]

            return unquote_plus(inp), url, isdir

    def _getBytes(self, inp, context):
        if context['isdir']:
            return 0

        inp = inp.strip()
        inp_tmp = ''.join([i for i in inp if not i.isdigit()])

        if not inp_tmp:
            try:
                return int(inp)
            except:
                return 0

        if not inp == '-':
            return human2bytes(inp)
