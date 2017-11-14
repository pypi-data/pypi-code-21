import re
import pytz
from datetime import datetime, date
from djtool.msgcode import tips
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils.timezone import utc
from django.utils import timezone
import importlib


try:
    from common.msgcode import tips as tip
    if not isinstance(tip, dict):
        tip = {}
except:
    tip = {}


class Common:

    @classmethod
    def _tips(cls, code):
        if isinstance(code, int):
            code = str(code)
        if code:
            if code in tips:
                return tips[code]
            elif code in tip:
                return tip[code]
            raise Exception('msg对应编码不存在')
        raise Exception('msg参数类型错误')

    @classmethod
    def msg(cls, code, data=None, **kwargs):
        result = {}
        result['code'] = int(code)
        result['msg'] = cls._tips(code) if 'remsg' not in kwargs else kwargs.get('remsg', '')
        if data is not None:
            result['data'] = data
        return result

    @classmethod
    def mobile(cls, no):
        if isinstance(no, int):
            no = str(no)
        if isinstance(no, str):
            no = no.strip()
            pattern = re.compile(
                '^(0|86|17951)?(13[0-9]|15[012356789]|18[0-9]|14[57]|17[0-9])[0-9]{8}$'
            )
            if pattern.match(no):
                return pattern.match(no).group()
            return None
        return None

    @classmethod
    def email(cls, email):
        if isinstance(email, str):
            email = email.strip()
            pattern = re.compile(
                '^\w+((-\w+)|(\.\w+))*\@[A-Za-z0-9]+((\.|-)[A-Za-z0-9]+)*\.[A-Za-z0-9]+$'
            )
            if pattern.match(email):
                return pattern.match(email).group()
            return None
        return None

    @classmethod
    def add_set(cls, a, b):
        if isinstance(a, list) and isinstance(b, list):
            return list(set(a) - set(b))
        return None

    @classmethod
    def del_set(cls, a, b):
        if isinstance(a, list) and isinstance(b, list):
            return list(set(b) - set(a))
        return None

    @classmethod
    def list_toInt(cls, a):
        b = []
        for i in a:
            if isinstance(i, int):
                b.append(i)
            else:
                b.append(int(i))
        return b

    @classmethod
    def page(cls, res, pg, **kwargs):
        paginator = Paginator(res, kwargs.get('pre', 10))
        try:
            page = paginator.page(pg)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)
        return page

    @classmethod
    def utcToLocal(cls, t):
        return t.replace(
            tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Shanghai'))

    @classmethod
    def localToUtc(cls, str):
        tz = pytz.timezone('Asia/Shanghai')
        a = tz.localize(datetime.strptime(str, '%Y-%m-%d %H:%M:%S')).astimezone(pytz.utc)
        return a

    @classmethod
    def localUtc(cls):
        return timezone.now().replace(tzinfo=utc)

    @classmethod
    def ID(cls, pg, i, **kwargs):
        return (int(pg) - 1) * kwargs.get('pre', 10) + i

    @classmethod
    def ID_desc(cls, total, pg, i, **kwargs):
        return total - ((int(pg) - 1) * kwargs.get('pre', 10) + i) + 1

    @classmethod
    def year(cls, front=0, back=0, text=''):
        year = datetime.today().year
        l = [(y, '%s%s' % (y, text)) for y in range(year-front, year+back)]
        return tuple(l)

    @classmethod
    def expire(cls, d):
        today = date.today()
        if (d - today).days >= 0:
            return False
        return True

    @classmethod
    def import_model(cls, config):
        s = config.split('.')
        j = '.'.join(s[:-1])
        return getattr(importlib.import_module(j), s[-1])
