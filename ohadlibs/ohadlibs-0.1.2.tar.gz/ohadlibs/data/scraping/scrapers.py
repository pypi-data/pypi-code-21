import re
import bs4
import requests


class HTMLTableScraper:

    def __init__(self, table):
        self.soup = table if "bs4" in str(table.__class__) else bs4.BeautifulSoup(table, 'html.parser')

    def parse(self):
        headers = []
        rows = []
        if self.soup.find("thead"):
            if len(self.soup.find("thead").find_all("th")) > 0:
                [headers.append(th.text.replace("\n", "").lower()) for th in self.soup.find("thead").find_all("th")]
        if self.soup.find("tbody"):
            if len(self.soup.find("tbody").find_all("tr")) > 0:
                [rows.append([str(td.text).replace("\n", "").strip() for td in tr.find_all("td")]) for tr in self.soup.find("tbody").find_all("tr")]
        return [dict(zip(headers, row)) for row in rows]

class BasicWebPageScraper:

    def __init__(self, url):
        self.regex = {
            'hashes': {
                'sha1': r'\b[a-f0-9]{40}\b',
                'md5': r'\b[a-fA-F\d]{32}\b',
                'sha256': r'\b[a-fA-F\d]{64}\b',
            }
        }
        self.init_url = url
        self.url = self.validate_url()
        self.request = requests.get(self.url)
        self.text = self.request.text
        self.soup = bs4.BeautifulSoup(self.text, 'html.parser')

    def validate_url(self):
        no_slash = [self.init_url[:-1] if self.init_url.endswith("/") else self.init_url][0]
        with_http = [no_slash if no_slash.startswith("http") else ''.join(["http://", no_slash])][0]
        return with_http

    def hrefs(self):
        hrefs = []
        for a in self.soup.find_all(href=True):
            try:
                try:
                    if a['href'].startswith("/"):
                        hrefs.append(''.join([self.url, a['href'][1:]]).encode("ascii"))
                    elif a['href'].find("tp://") > -1:
                        hrefs.append(a['href']).encode("ascii")
                except AttributeError:
                    continue
            except TypeError:
                continue
        return list(set(hrefs))

    def downloads(self, extensions):
        base_extensions = ['zip', 'rar', '7z']
        if type(extensions) == str:
            base_extensions.append(extensions)
        else:
            extensions += base_extensions
            download_hrefs = []
            for href in self.hrefs():
                for extension in extensions:
                    if str(href).endswith(".{}".format(extension)):
                        download_hrefs.append(href)
            return list(set(download_hrefs))

    def hashes(self):
        results = {}
        for _hash in self.regex['hashes']:
            results[_hash] = list(set(re.findall(self.regex['hashes'][_hash], self.text)))
        return results
