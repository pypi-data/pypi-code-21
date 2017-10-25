"""
 # Copyright (c) 07 2016 | suryakencana
 # 7/12/16 nanang.ask@kubuskotak.com
 #  fields
"""
import json
from collections import namedtuple

from webhelpers2.html import tags, HTML

from .utils import gen_id, format_date, get_date_format, format_datetime, get_datetime_format

tool = namedtuple('tool', ('name', 'url', 'icon', 'title', 'with_row'))


class _Option(tags.Option):
    """private Option class for backward compatible
    """
    def __init__(self, value=None, label=None):
        super(_Option, self).__init__(label, value)


def _combotree_field(
        name, value, url, sort, order='asc', data_options=None, **kwargs
):
    _data_options = """
        url: '{url}',
        onBeforeLoad: function(node, param){
            param.sort = '{sort}';
            param.order = '{order}';
    """ % dict(url=url, sort=sort, order=order)
    if value:
        _data_options += """
            if(!node){
                param.id = {id};
                param.with_chain = true;
            }
        """ % {id: value}

    _data_options += """
        }
    """
    if value:
        _data_options += """,
            onLoadSuccess: function(node, data){
                if(!node){
                    var n = $(this).tree('find', %s);
                    $(this).tree('expandTo', n.target);
                    $(this).tree('scrollTo', n.target);
                }
            }
        """ % value
    if data_options:
        _data_options += ',%s' % data_options

    return tags.text(
        name, value, class_="easyui-combotree text w20",
        data_options=_data_options, **kwargs
    )


def status_combobox_field(name, options,
                          value=None, data_options=None, **kwargs):

    _data_options = "panelHeight:'auto',editable:false,width:175"
    if data_options:
        _data_options += ",%s" % data_options

    return tags.select(
        name, value, map(lambda x: _Option(*x), options),
        class_='easyui-combobox text w10',
        data_options=_data_options, **kwargs
    )


class _ComboBox(object):
    def __init__(self, name, options,
                 value=None, data_options=None, **kwargs):
        self._data_options = "panelHeight:'auto',editable:false,width:175"
        self.name = name
        self.options = options
        self.value = value

        if data_options:
            self._data_options += ",%s" % data_options

    def __call__(self, *args, **kwargs):
        return tags.select(
            self.name, self.value, map(lambda x: _Option(*x), self.options),
            class_='easyui-combobox text w10',
            data_options=self._data_options, **kwargs
        )


def yes_no_field(name, value=None, data_options=None, **kwargs):
    choices = [
        _Option(0, _(u'no')),
        _Option(1, _(u'yes')),
    ]
    _data_options = "panelHeight:'auto',editable:false"
    if data_options:
        _data_options += (',%s' % data_options)
    return tags.select(
        name, value, choices, class_='easyui-combobox text w5',
        data_options=_data_options, **kwargs
    )


def switch_field(name, value=None, data_options=None, **kwargs):
    _data_options = ""
    if data_options:
        _data_options += ('%s' % data_options)
    return tags.checkbox(
        name, True, bool(value), class_='easyui-switchbutton',
        data_options=_data_options, **kwargs
    )


def date_field(name, value=None, data_options=None, **kwargs):
    _id = gen_id()
    format = get_date_format()

    # this hack is need for datebox correct working
    format = format.replace('yy', 'yyyy')

    _data_options = """
        editable:false,
        formatter:function(date){return kara.ui.helpers.dt_formatter(date, %s);},
        parser:function(s){return kara.ui.helpers.dt_parser(s, %s);}
        """ % (
        json.dumps(format),
        json.dumps(format)
    )
    if data_options:
        _data_options += ",%s" % data_options
    if value:
        value = format_date(value, format)
    html = tags.text(
        name, value, class_="easyui-datebox text w10",
        id=_id, data_options=_data_options, **kwargs
    )
    return html + HTML.literal("""
        <script type="text/javascript">
            kara.ui.helpers.add_datebox_clear_btn("#%s");
        </script>
    """) % _id


def datetime_field(name, value=None, data_options=None, **kwargs):
    _id = gen_id()
    _data_options = """
        editable:false,
        showSeconds:false,
        formatter:function(date){return dt_formatter(date, %s);},
        parser:function(s){return dt_parser(s, %s);}
        """ % (
        json.dumps(get_datetime_format()),
        json.dumps(get_datetime_format())
    )
    if data_options:
        _data_options += ",%s" % data_options
    if value:
        value = format_datetime(value)
    html = tags.text(
        name, value, class_="easyui-datetimebox text w10",
        id=_id, data_options=_data_options, **kwargs
    )
    return html + HTML.literal("""
        <script type="text/javascript">
            add_datetimebox_clear_btn("#%s");
        </script>
    """) % _id

    #
    # def services_types_combobox_field(request, name, value=None):
    #     session = request.db
    #     ids = map(
    #         lambda x: str(x.id), get_resources_types_by_interface(session, IServiceType)
    #     )
    #     data_options = """
    #         url: '/resources_types/list',
    #         valueField: 'id',
    #         textField: 'humanize',
    #         editable: false,
    #         onBeforeLoad: function(param){
    #             param.sort = 'humanize';
    #             param.rows = 0;
    #             param.page = 1;
    #             param.id = %s
    #         },
    #         loadFilter: function(data){
    #             return data.rows;
    #         }
    #     """ % json.dumps(','.join(ids))
    #     return tags.text(
    #         name, value, class_="easyui-combobox text w20",
    #         data_options=data_options
    #     )