# -*- coding:utf-8 -*-
from django_szuprefix.utils import excelutils

__author__ = 'denishuang'
from django.utils.functional import cached_property
from .validators import format_split_by_bracket, format_banjiao, field_userid
import logging

log = logging.getLogger("django")


class RecordDict(dict):
    def __init__(self, **kwargs):
        self.errors = []
        self.warnings = []
        return super(RecordDict, self).__init__(**kwargs)


class BaseImporter(object):
    fields = []
    min_fields_count = 1
    extra_cleans = []
    required_fields = []

    @cached_property
    def synonyms_map(self):
        r = {}
        for f in self.fields:
            for s in f.get_synonyms() + [f.name]:
                r[s] = f
        return r

    def _sort_field_names(self, fs):
        fns = [f.name for f in self.fields]
        r = [n for n in fns if n in fs]
        r += [n for n in fs if n not in r]
        return r

    def clean_no_duplicate(self, data):
        # kfn = self.key_field and self.key_field.name
        # if not kfn:
        #     return
        no_duplicate_field_names = [f.name for f in self.fields if f.no_duplicate]
        m = {}
        for d in data:
            for f in no_duplicate_field_names:
                m.setdefault(f, {})
                mf = m[f]
                v, e = d.get(f, (None, None))
                if not v:
                    continue
                if v in mf:
                    e.append("重复")
                    d.errors.append("%s重复" % f)
                    d2 = mf.get(v)
                    d2[f][1].append("重复")
                    d2.errors.append("%s重复" % f)
                mf[v] = d

    def clean(self, data):
        r = []
        fs = set()
        for i in data:
            d = self.clean_item(i)
            r.append(d)
            fs.update(d.keys())
        self.clean_no_duplicate(r)
        r.sort(key=lambda x: x.errors, reverse=True)
        return {"data": r, "fields": self._sort_field_names(fs)}

    def get_cleaned_data(self, data):
        for d in self.clean(data)["data"]:
            obj = dict([(k, v[0]) for k, v in d.items() if not v[1]])
            yield obj

    def clean_item(self, obj):
        r = RecordDict()
        m = self.synonyms_map
        for k, v in obj.items():
            k = format_split_by_bracket(format_banjiao(k))
            if k == "import_results":
                continue
            f = m.get(k)
            if f:
                n, v, e = f(v)
            else:
                n, e = k, []
            if e:
                r.errors += e
            r[n] = (v, e)
        for f in self.extra_cleans:
            f(r)
        for f in self.required_fields:
            n = f.name
            if n in r:
                continue
            e = [u"必填"]
            r[n] = ("", e)
            r.errors += e
        return r

    def get_excel_data(self, excel):
        return excelutils.excel2json(excel, field_names_template=self.synonyms_map.keys(), min_fields_count=self.min_fields_count,
                          col_name_formater=format_split_by_bracket)

    def extra_action(self, api, worker, created):
        return True

    def run(self, data, corp):
        if not isinstance(data, dict):
            data = self.clean(self.get_excel_data(data))
        fs = data.get("fields")
        ds = data.get("data")
        ds = [dict([(k, v[0]) for k, v in o.items()]) for o in ds]
        ct = cc = cu = ce = 0
        for d in ds:
            ir = []
            try:
                worker, created = self.import_one(d)
                if created:
                    cc += 1
                    ir.append(u"创建成功;")
                else:
                    cu += 1
                    ir.append(u"更新成功;")

            except Exception, e:
                log.error("%s run error:%s; data:%s", self, e, d)
                ce += 1
                ir.append(u"程序异常;")
            d["import_results"] = ir
            ct += 1
        fs.append("import_results")
        return {"count": {"total": ct, "create": cc, "update": cu, "error": ce}, "data": ds, "fields": fs}

    def import_one(self, api, data):
        raise Exception("unimplemented!")


# class WorkerImporter(BaseImporter):
#     fields = [field_han, field_mobile, field_weixinid]
#

# class ExtattrImporter(BaseImporter):
#     fields = [field_userid]
#
#     def import_one(self, api, d):
#         wx_userid = d.get(u"帐号")
#         worker = api.corp.workers.get(wx_userid=wx_userid)
#         worker.update_extattr(dict([(k, v) for k, v in d.iteritems() if k <> u"帐号"]))
#         return worker, False
