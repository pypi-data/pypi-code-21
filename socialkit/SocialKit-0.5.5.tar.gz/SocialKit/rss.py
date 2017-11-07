import base64
from qlib.data.sql import SqlObjectEngine, Table, SqlEngine
from qlib.asyn import Exe
from .parser import XmlParser
from .log import show, logging, colored, L
from .libs import  send_and_reciv
from os import mkdir
from os import getenv
import os,time


class RssResource(Table):
    resfrom = str
    geo = str
    about = str
    url = str

    def __repr__(self):
        return self.geo + "|" + self.url


class Rss(Table):
    title = str
    pubDate = str
    lang = str
    descr = str

    def __repr__(self):
        return self.title + "|" + self.pubDate


class RssContent(Table):
    content = 'None'
    title = str
    link = str
    pubDate = str
    descr = str
    belongto = Rss

    def __repr__(self):
        return self.title + "|" + self.pubDate


class RssTag(Table):
    name = str
    belongto = RssContent

    def __repr__(self):
        return self.name + " | " + str(self.belongto)

class ItemDoc:

    def __init__(self, item, category=None):
        self.category = set()
        if isinstance(item, RssContent):
            for i in item._columns():
                if 'desc' in i:
                    setattr(self, i, base64.b64decode(getattr(item, i)).decode('utf8'))
                    continue
                setattr(self, i, getattr(item, i))
            if category:
                self.category = category
        else:
            for i in item.iter():
                if ':'  in i.tag:
                    continue
                if i.tag == 'category':
                    self.category.add( next(i.itertext()) )
                    continue

                setattr(self, i.tag, next(i.itertext()))

    def __getitem__(self, k):
        for t in self.category:
            if k in t:
                return True
        if len(self.description.split(k)) > 2:
            return True

        return False

    def save(self, rss_handler, rssbelong):
        rss_handler.save('C', title = self.title, pubDate= self.pubDate, link=self.link, descr = self.description, belongto = rssbelong)
        this = rss_handler._db.last(RssContent, pubDate= self.pubDate, link=self.link)
        for t in self.category:
            rss_handler.save('T',name=t, belongto=this)

    def __repr__(self):
        return self.title + " | " + self.pubDate

class RssDoc:

    def __init__(self, rss_handler, xml_content):
        self.title = xml_content("channel > title").text()
        self.descr = xml_content("channel > description").text()
        self.lang = xml_content("channel > language").text()
        self.pubDate = xml_content("channel > pubDate").text()
        self.items = [ItemDoc(i) for i in xml_content("channel > item")]
        self.rss_handler = rss_handler

    def __getitem__(self, k):
        for i in self.items:
            if i[k]:
                yield i

    def save(self):
        self.rss_handler.save('D' ,title=self.title, pubDate = self.pubDate, lang=self.lang, descr=self.descr)
        belongtoRss = self.rss_handler._db.last(Rss, title=self.title)
        if belongtoRss:
            [i.save(self.rss_handler, belongtoRss) for i in self.items ]


    def __repr__(self):
        return self.title + " | " + self.pubDate

class NoC:
    def __init__(self, url):
        self.url = url

    def save(self):
        logging.debug(colored("failed got " + self.url,'red'))

class RssHandler:

    def __init__(self, database=None):
        self.database = database
        self._db = SqlObjectEngine(database=database)
        HOME = getenv("HOME")
        self.download_root = os.path.join(HOME, 'rss-cache')
        self.now = 0
        try:

            self._db.create(Rss)
            self._db.create(RssResource)
            self._db.create(RssContent)
            self._db.create(RssTag)
            
            
            
        except Exception as e:
            pass

        try:
            mkdir(self.download_root)
        except Exception as e:
            pass

    def load(self, type, **condition):
        if type == 'C':
            c = RssContent
        elif type == 'D':
            c = Rss
        elif type == 'R':
            c = RssResource
        elif type == 'T':
            c = RssTag
        else:
            raise Exception("not support this type , only C/T/R .")
        
        res = self._db.find(c, **condition)
        return res

    def save(self, type, **kargs):
        if type == 'C':
            c = RssContent
        elif type == 'D':
            c = Rss
        elif type == 'R':
            c = RssResource
        elif type == 'T':
            c = RssTag
        else:
            raise Exception("not support this type , only C/T/R .")
        for i in kargs:
            if 'desc' in i:
                kargs[i] = base64.b64encode(kargs[i].encode()).decode("utf8")
        r = c(**kargs)
        if not self._db.find_one(c, **kargs):
            self._db.add(r)
            return True
        else:
            return False

    def parse(self, xml_content):
        if not isinstance(xml_content, bytes):
            return RssDoc(self, XmlParser(xml_content.encode()))
        return RssDoc(self, XmlParser(xml_content))

    def list(self):
        return [i for i in self.load('R')]


    def list_cate(self):
        return [i for i in self.load("T")]

    def list_resource(self):
        return [i for i in self.load("R")]        

    def update(self, requester, url=None):
        e = Exe(10)
        

        def req(url, parse, requester):
            try:

                r = parse(requester(url))
                return r,url
            except AttributeError:
                return NoC(url), url


        if url:
            res = self.parse(requester(url))
            res.save()
        else:
            args = []
            for r in self.list_resource():
                args.append([r.url, self.parse, requester])

            for r,url in e.map(req, args):
                r.save()
                show("update | " + url)


    def __getitem__(self,k):
        res = {}

        for tag in self._db.sql.search("RssTag",'belongto',name=k):
            i = ItemDoc(self._db.find_one(RssContent, ID=tag[0]))
            if i.__repr__() not in res:
                res[i.__repr__()] = i
        return list(res.values())

    def _down(self,link, down_root, one, req):
        self.now += 1
        try:
            m = req(link)
        except Exception as e:
            show(e,color='red')
            return None, down_root, one

        if m:
            x = XmlParser(m)
            return x, down_root,one
        else:
            return None, down_root, one

    def _save(self,x,download_root, one):
        if x:
            try:
                with open(os.path.join(download_root, one.title), 'w') as fp:
                    fp.write(x.text)
                    logging.debug("download: "+ colored(one.title,'green'))
                    L(colored('->','green'),one.title, end='\r', c='cyan')
            except FileNotFoundError as e:
                L(colored('save-error | ','red'), one.title)
        else:
            logging.debug("download failed" + colored(one.title,'red'))
            L(colored('x','red'),one.title, c='red')
        self.now -= 1

    def download(self, link, req):
        e = Exe(10)

        one = next(self.load('C', link=link))
        files = os.listdir(self.download_root)
        if one.title not in files:
        # hash_str = md5(one.__repr__().encode('utf8')).hexdigest()
        
            logging.debug(colored(link, 'yellow'))
            e.done(self._down,self._save, one.link, self.download_root, one,req)
        else:
            logging.debug(colored(one.link,'red'))
            
            return True
        return False

    def download_check(self,req, url=None):
        q = set()
        for i in self.load('C'):
            if url:
                if url in i.link:
                    q.add(i.link)
                    continue
            q.add(i.link)

        
        if len(q) == 0:
            logging.debug(colored('no update','red'))
        while  len(q):
            r = q.pop()
            if self.now < 10:
                self.download(r, req)
            else:
                time.sleep(1)

    def __del__(self):
        self._db.close()


def default_req(url, password='fuck this', proxy='localhost:9000'):
    return send_and_reciv(password.encode('utf8'), url, proxy)