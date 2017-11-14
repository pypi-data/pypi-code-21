# -*- coding:utf-8 -*-
import re
import urllib

from pyquery import PyQuery
import lxml.html
from yandex_parser.exceptions import EmptySerp, YandexParserError
from yandex_parser.utils import to_unicode, get_full_domain_without_scheme
from lxml import etree


class YandexParser(object):
    params_regexr = re.U | re.M | re.DOTALL | re.I

    patterns = {
        'pagecount': re.compile(u'found"\:"&mdash;&nbsp;(.*?)отв', params_regexr),
        'infected': re.compile(u'/search/infected/?\?url=([^&]+)', params_regexr),
        'captcha': re.compile(u'<img class="image form__captcha".*?src=\"([^\"]+)\"', params_regexr),
    }

    USE_IGNORE_BLOCK = True

    PAGECOUNT_PATTERNS = (
        re.compile(u'found"\:"&mdash;&nbsp;(.*?)отв', params_regexr),
        re.compile(ur'"found":"[^\\]\\n([^"]*?)отв', params_regexr),
        re.compile(ur'<div class="serp-adv__found">Наш[^ ]+\s+(.*?)рез', params_regexr)
    )

    def __init__(self, content, snippet_fileds=('d', 'p', 'u', 't', 's', 'm')):
        self.content = to_unicode(content)
        self.snippet_fileds = snippet_fileds

    def get_context_snippet_title(self, content):
        res = re.search(ur'<h2[^>]*?>\s*<a[^>]*?href="([^"]+?)"[^>]*?>\s*(.*?)\s*</a>', content, re.I | re.M | re.S)
        if not res:
            raise YandexParserError(u'Не удалось распарсить тайтл в сниппете: {0}'.format(content))
        return {'u': res.group(1), 't': YandexParser.strip_tags(res.group(2))}

    def get_context_visible_url(self, sn):
        els = sn.xpath('.//div[contains(@class,"typo_type_greenurl")]/div/a')
        if not els:
            return ''
        return unicode(els[0].text_content())

    def _get_context_snippet_area(self, sn, is_top):
        top_or_bot = sn.xpath('.//div[contains(@class,"typo_type_greenurl")]/div[contains(@class,"label_color_yellow")]')
        if not top_or_bot:
            return 'r'

        if is_top:
            return 't'

        return 'b'


    def get_context_serp(self):
        result = []
        is_top = True
        old_class = None

        dom = PyQuery(self.content)
        serp = dom('.serp-item')
        for sn in serp:
            is_ignore_block = self._ignore_block(sn)
            is_context_snippet = self._is_context_snippet(sn)

            if not is_ignore_block:
                is_top = False
                continue

            if not is_context_snippet:
                continue

            t_or_b = sn.xpath('.//div[contains(@class,"typo_type_greenurl")]/div[contains(@class,"label_color_yellow")]') \
                or sn.cssselect('li.serp-adv-item div.organic__subtitle')
            if t_or_b:
                cur_class = filter(lambda x: re.match(ur'data-[\w\d]{4,}', x), sn.attrib)[0]
                if old_class and cur_class != old_class:
                    is_top = False
                old_class = cur_class

            if not t_or_b:
                a = 'r'
            elif is_top:
                a = 't'
            else:
                a = 'b'

            title, url = self._get_title(sn, False)
            item = {'u': url, 't': title}
            item['vu'] = self.get_context_visible_url(sn)
            item['a'] = a
            result.append(item)

        return {'pc': len(result), 'sn': result}

    def get_serp(self):
        if self.is_not_found():
            return {'pc': 0, 'sn': []}

        if not YandexParser.is_yandex(self.content):
            raise YandexParserError(u'content is not yandex')

        pagecount = self.get_pagecount()
        snippets = self.get_snippets()
        
        if not snippets:
            raise EmptySerp()
        
        return {'pc': pagecount, 'sn': snippets}

    def pagination_exists(self):
        return '<span class="pager__group">' in self.content

    @classmethod
    def is_yandex(cls, content):
        return '<a class="logo__link" href="//www.yandex.' in content or u'<title>Яндекс' in content

    def get_clean_html(self):
        return YandexSerpCleaner.clean(self.content)

    def get_pagecount(self):
        if self.is_not_found():
            return 0

        match = None
        for pattern in self.PAGECOUNT_PATTERNS:
            match = pattern.search(self.content)
            if match:
                break

        if not match:
            return

        pagecount_raw = match.group(1)
        pagecount = int(pagecount_raw.split()[0])
        if u'тыс' in pagecount_raw:
            pagecount *= 1000
        elif u'млн' in pagecount_raw:
            pagecount *= 1000000
        return pagecount

    def is_not_found(self):
        return u'По вашему запросу ничего не нашлось' in self.content

    def _get_title_h2(self, sn, is_video_snippet):
        if is_video_snippet:
            return sn.xpath('.//div[contains(@class,"video2 ")]')[0]

        return sn.find('.//h2')

    def _get_url_from_mobile_greenurl(self, sn):
        div = sn.xpath('.//div[contains(@class,"typo_type_greenurl")]')
        if not div:
            raise YandexParserError(u'Тайтла нет, div greenurl - нет')

        url = div[0].xpath('.//a')
        if not url:
            raise YandexParserError(u'Тайтла нет, greenurl - нет')
        return url[0].attrib['href']

    def _get_true_url(self, sn, url):
        #Яндекс жжет. Берем домен из гринурла
        infected = False

        if url == 'http://':
            html = etree.tostring(sn)
            pattern = re.compile(ur'<div class="serp-item__greenurl.*?<a class="link serp-url__link".*?>(.*?)</a>', re.I | re.M | re.S)
            res = pattern.search(html)
            if res:
                domain = re.sub(ur'<[^>]+>', '', res.group(1), flags=re.I | re.M | re.S)
                domain = re.sub(ur'\s+', '', domain, flags=re.I | re.M | re.S)
                url = 'http://{}'.format(domain)

        if 'infected' in url:
            match_url_infected = self.patterns['infected'].match(url)
            if match_url_infected:
                url = urllib.unquote(match_url_infected.group(1))
                infected = True

        return url, infected

    def _get_title(self, sn, infected):
        is_video_snippet = 't-construct-adapter__free-video' in sn.attrib['class']

        h2 = self._get_title_h2(sn, is_video_snippet)
        if not h2:
            return None, self._get_url_from_mobile_greenurl(sn)

        if infected:
            link = h2
            url = self._get_infected_url(sn)
        else:
            link = h2.find('a')
            url = link.attrib['href']

        if is_video_snippet:
            title = unicode(sn.find('.//*[@class="video2__title"]').text_content())
        else:
            title = unicode(link.text_content())

        return title, url

    def _get_infected_url(self, sn):
        div = sn.find('.//*[@class="template-infected__unsafe"]')
        if div:
            return div.find('a').attrib['href']

        h2 = sn.find('.//h2')
        if h2:
            return h2.find('a').attrib['href']

        raise YandexParserError(u'Not found infected url')

    def _get_domain(self, url):
        try:
            domain = get_full_domain_without_scheme(url)
        except UnicodeError as e:
            raise e

        if ':' in domain:
            domain = re.sub(ur':\d+$', '', domain)
        return domain

    def _is_context_snippet(self, sn):
        return 'serp-adv' in sn.attrib['class'] or 't-construct-adapter__adv' in sn.attrib['class']

    def _ignore_block(self, sn):
        if self._is_context_snippet(sn):
            return True

        if 'z-' in sn.attrib['class'] \
            or 'template-object-badge' in sn.attrib['class']\
            or 't-construct-adapter__companies' in sn.attrib['class']:
            #реклама
            return True

        # игнорим новости
        if 't-construct-adapter__news' in sn.attrib['class']:
            return True

        # игнорим "расписание, результаты и трансляции на Яндексе"
        if 't-sport-' in sn.attrib['class']:
            return True

        # игнорим предложения на маркете
        if 't-market-offers' in sn.attrib['class']:
            return True

        if 't-construct-adapter__market-' in sn.attrib['class']:
            return True

        # игнорим картинки
        if 't-construct-adapter__images' in sn.attrib['class']:
            return True

        # игнорим видео
        if 't-construct-adapter__video' in sn.attrib['class']:
            return True

        # игонорим тизеры
        if sn.xpath('.//div[contains(@class,"teaser ")]'):
            return True

        # игнорим текущий счет спортивных соревнований
        if 't-construct-adapter__sport-livescore' in sn.attrib['class']:
            return True

        # игнорим номера регионов
        if 't-construct-adapter__auto-regions' in sn.attrib['class']:
            return True

        # игнорим факты
        if re.search(ur't-construct-adapter__.+-fact', sn.attrib['class'], re.I):
            return True

        # почтовые индексы
        if 't-post-indexes' in sn.attrib['class']:
            return True

        # описание местности
        if 't-construct-adapter__entity-card' in sn.attrib['class']:
            return True

        # Похожее описание местности
        if 't-construct-adapter__entity-homonym' in sn.attrib['class']:
            return True

        # игнорим конвертер единиц
        div = sn.find('div')
        if div and 'z-' in div.attrib['class']:
            return True

        # На ваш запрос можно дать короткий и однозначный ответ?
        if 't-construct-adapter__ugc' in sn.attrib['class']:
            return True

        # конвертер
        if 't-construct-adapter__units-converter' in sn.attrib['class']:
            return True

        # калькулятор
        if 't-construct-adapter__calculator' in sn.attrib['class']:
            return True

        # реновация
        if 't-construct-adapter__demolition' in sn.attrib['class']:
            return True

        # Вы нашли то, что искали
        if 'ugc-item' in sn.attrib['class']:
            return True

        return False

    def get_snippets(self):

        try:
            dom = PyQuery(self.content)
            serp = dom('.serp-list').children('.serp-item')

            snippets = []
            position = 0
            for sn in serp:
                if self.USE_IGNORE_BLOCK and self._ignore_block(sn):
                    continue

                infected = 'template-infected' in sn.attrib['class']

                title, url = self._get_title(sn, infected)

                url, url_infected = self._get_true_url(sn, url)
                infected |= url_infected

                domain = self._get_domain(url)

                position += 1

                snippet = {
                    'd': domain,
                    'domain': domain,
                    'p': position,
                    'u': url,
                    'm': url.startswith('http://maps.yandex.ru'),
                    't': None,  # title snippet
                    's': None,  # body snippet
                    'i': infected,
                    'savedCopy': None,
                    'fl': self._get_fl(sn)
                }

                if 't' in self.snippet_fileds:
                    snippet['t'] = title

                if 's' in self.snippet_fileds:
                    decr_div = sn.xpath('.//div[contains(@class,"serp-item__text")]') \
                                or sn.xpath('.//div[contains(@class,"serp-item__data")]') \
                                or sn.xpath('.//div[contains(@class,"social-snippet2__text")]') \
                                or sn.xpath('.//div[contains(@class,"organic__text")]') \
                                or sn.xpath('.//div[contains(@class,"extended-text__short")]') \
                                or sn.xpath('.//div[@class="text"]')

                    snippet['s'] = unicode(decr_div[0].text_content()) if decr_div else ''
                    snippet['s'] = snippet['s'] or ''
                div_saved_copy_link = sn.xpath('.//div[contains(@class,"popup2")]')
                if div_saved_copy_link:
                    attrib = div_saved_copy_link[0].find('a')
                    if attrib and 'href' in attrib.attrib:
                        snippet['savedCopy'] = attrib.attrib['href']
                    else:
                        snippet['savedCopy'] = None

                snippets.append(snippet)
            result = snippets

            pagecount = self.get_pagecount()
            len_snippets = len(snippets)
            if pagecount > 50 and len_snippets % 10 != 0:
                cut_snippets = []
                # в этом случае убираем поддомены яндекса из серпа, так чтобы получилось число кратное 10
                need_delete = len_snippets - len_snippets / 10  * 10
                p = 0
                for sn in snippets:
                    if need_delete and re.search(ur'^(?:.+\.|)yandex\.ru$', sn['d'], re.I):
                        need_delete -= 1
                        continue
                    p += 1
                    sn['p'] = p
                    cut_snippets.append(sn)
                result = cut_snippets
        except Exception as e:
            raise YandexParserError(str(e))

        return result

    def _get_fl(self, sn):
        els = sn.xpath('.//span[contains(@class,"serp-meta__item")]')
        if not els:
            return 0
        span_text = els[0].text_content() or ''
        return int(span_text.lower() == u'Ссылки на страницу содержат:'.lower())


    def get_region_code(self, default=None):
        dom = PyQuery(self.content)
        inputs = dom.find('input[name=rstr]')
        if inputs:
            return int(inputs[0].attrib['value'].lstrip('-'))
        return default

    def get_captcha_data(self):
        if 'checkcaptcha' not in self.content:
            return

        match_captcha = self.patterns['captcha'].findall(self.content)
        url_image = match_captcha[0]
        html = lxml.html.fromstring(self.content)
        form = html.forms[0]
        form_data = dict(form.form_values())

        return {
            'url': url_image,
            'form_action': form.action,
            'form_data': form_data,
        }

    @classmethod
    def strip_tags(self, html):
        return re.sub(ur' {2,}', ' ', re.sub(ur'<[^>]*?>', '', html.replace('&nbsp;', ' '))).strip()


class YandexSerpCleaner(object):
    flags = re.U | re.I | re.M | re.S

    _patterns = (
        ur'<script.*?<\/script>',
        ur'<style.*?<\/style>',
        ur'onmousedown\s*=\s*".*?"',
        ur'onclick\s*=\s*".*?"',
        ur'target\s*=\s*"_blank"',
        ur'title\s*=\s*".*?"',
        ur'ondblclick=".*?"',
        ur'style=".*?"',
        ur'<noscript>.*?<\/noscript>',
        ur'<link.*?/>',
        ur'<!--.*?-->',
        ur'<i\s+><\/i>',
        ur'data-bem\s*=\s*"[^"]*?"',
        ur"data-bem\s*=\s*'[^']*?'",
        ur'content\s*=\s*"[^"]*?"',
        ur'data-counter\s*=\s*"[^"]*?"',
        ur"data-counter\s*=\s*'[^']*?'",
        ur"data-log-node=[^ >]*",
        ur'\r|\n',
        ur' {2,}',
    )
    patterns = []
    for p in _patterns:
        patterns.append(re.compile(p, flags=re.U | re.I | re.M | re.S))
    patterns = tuple(patterns)

    no_space = re.compile(ur'\s+', flags=flags)

    @classmethod
    def clean(cls, content):
        content = content
        for p in cls.patterns:
            content = p.sub('', content)

        content = cls.no_space.sub(' ', content)
        return content
