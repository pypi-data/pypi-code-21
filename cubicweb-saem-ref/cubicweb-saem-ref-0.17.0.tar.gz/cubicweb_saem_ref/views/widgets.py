# copyright 2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-saem-ref custom widgets"""

import calendar
from datetime import datetime

from six import text_type
from dateutil.parser import parse as parse_date

from logilab.common.date import ustrftime

from cubicweb import tags
from cubicweb.utils import JSString, json_dumps
from cubicweb.uilib import js
from cubicweb.web import ProcessFormError, formwidgets as fw
from cubicweb.web.views import ajaxcontroller


def process_incomplete_date(datestr, end=False):
    """Parse a date from a string.

    Return the date if the given string is a valid date, else if only the year or the year and the
    month is given, return a date completed with default day and/or month value:

    * if end is True, default day/month is 31/12 and default day is the last day of the given month
    * if end is False, default day/month is 01/01 and default day is 1
    """
    if not datestr:
        return None
    if end:
        if len(datestr.split("/")) == 2:  # = day is not defined
            pdate = parse_date(datestr, default=datetime(9999, 12, 1), dayfirst=True)
            last_day = calendar.monthrange(pdate.year, pdate.month)[1]
            pdate = pdate.replace(day=last_day)
        else:
            pdate = parse_date(datestr, default=datetime(9999, 12, 31), dayfirst=True)
    else:
        pdate = parse_date(datestr, default=datetime(9999, 1, 1), dayfirst=True)
    if pdate.year == 9999:
        raise ValueError()
    return pdate.date()


class JQueryIncompleteDatePicker(fw.JQueryDatePicker):
    """Custom datefield enabling the user to enter only the year or the month and year
    of the date.

    If only the year or the year and the month is given, behaviour will change depending on the
    `default_end` boolean flag:

    * when true, default month is december and default day is the last day of the given month
    * when false, default month is january and default day is 1
    """
    def __init__(self, *args, **kwargs):
        self.default_end = kwargs.pop("default_end", False)
        self.update_min = kwargs.pop("update_min", None)
        self.update_max = kwargs.pop("update_max", None)
        super(JQueryIncompleteDatePicker, self).__init__(*args, **kwargs)

    def process_field_data(self, form, field):
        datestr = form._cw.form.get(field.input_name(form))
        try:
            return process_incomplete_date(datestr, self.default_end)
        except ValueError as exc:
            if "day is out of range for month" in exc:
                raise ProcessFormError(form._cw._("day is out of range for month"))
            elif "month must be in 1..12" in exc:
                raise ProcessFormError(form._cw._("month must be in 1..12"))
            else:
                raise ProcessFormError(form._cw._("can not process %s: expected format "
                                                  "dd/mm/yyyy, mm/yyyy or yyyy" % datestr))

    def attributes(self, form, field):
        attrs = super(JQueryIncompleteDatePicker, self).attributes(form, field)
        form._cw.add_js('cubes.saem_ref.js')
        if self.update_max:
            domid = '%s-subject:%s' % (self.update_max, form.edited_entity.eid)
            attrs['onChange'] = js.saem.update_datepicker_minmax(domid, 'maxDate',
                                                                 JSString('this.value'))
        if self.update_min:
            domid = '%s-subject:%s' % (self.update_min, form.edited_entity.eid)
            attrs['onChange'] = js.saem.update_datepicker_minmax(domid, 'minDate',
                                                                 JSString('this.value'))
        return attrs

    def _render(self, form, field, renderer):
        req = form._cw
        if req.lang != 'en':
            req.add_js('jquery.ui.datepicker-%s.js' % req.lang)
        domid = field.dom_id(form, self.suffix)
        # XXX find a way to understand every format
        fmt = req.property_value('ui.date-format')
        picker_fmt = fmt.replace('%Y', 'yy').replace('%m', 'mm').replace('%d', 'dd')
        max_date = min_date = None
        if self.update_min:
            current = getattr(form.edited_entity, self.update_min)
            if current is not None:
                max_date = ustrftime(current, fmt)
        if self.update_max:
            current = getattr(form.edited_entity, self.update_max)
            if current is not None:
                min_date = ustrftime(current, fmt)
        req.add_onload(u'cw.jqNode("%s").datepicker('
                       '{buttonImage: "%s", dateFormat: "%s", firstDay: 1,'
                       ' showOn: "button", buttonImageOnly: true, minDate: %s, maxDate: %s});'
                       % (domid, req.uiprops['CALENDAR_ICON'], picker_fmt, json_dumps(min_date),
                          json_dumps(max_date)))
        return self._render_input(form, field)


class ConceptAutoCompleteWidget(fw.TextInput):
    """Derive from simple text input to create an autocompletion widget if some scheme is specified.
    Otherwise, free text is fine if `optional` argument is true. In such case:

    * `slave_name` is expected to be the name of the text attribute

    * you'll have to use this widget from a custom field that will handle the relation to the
      concept(see example in agent views).
    """

    def __init__(self, slave_name, master_name, optional=False, **kwargs):
        super(ConceptAutoCompleteWidget, self).__init__(**kwargs)
        self.slave_name = slave_name
        self.master_name = master_name
        self.optional = optional

    def _render(self, form, field, render):
        entity = form.edited_entity
        slave_id = field.dom_id(form, self.suffix)
        master_id = slave_id.replace(self.slave_name, self.master_name)
        if entity.has_eid():
            concept = entity.concept
        else:
            concept = None
        req = form._cw
        req.add_js(('cubicweb.js', 'cubicweb.ajax.js', 'cubes.saem_ref.js'))
        req.add_onload(js.saem.initSchemeConceptFormField(master_id, slave_id))
        if concept is None:
            value = getattr(entity, self.slave_name) if self.optional else None
            eid = u''
        else:
            if concept.cw_etype == 'Concept':
                value = concept.label()
            else:  # ExternalURI
                value = concept.dc_title()
            eid = text_type(concept.eid)
        # we need an hidden input to handle the value while the text input display the label
        inputs = [
            tags.input(name=field.input_name(form, 'Label'), id=slave_id + 'Label',
                       klass='form-control', type='text',
                       value=value),
            tags.input(name=field.input_name(form), id=slave_id, type='hidden',
                       value=eid)
        ]
        return u'\n'.join(inputs)


@ajaxcontroller.ajaxfunc(output_type='json')
def keyword_concepts(self):
    assert self._cw.form['scheme']
    scheme = int(self._cw.form['scheme'])
    term = self._cw.form['q']
    limit = self._cw.form.get('limit', 50)
    return [{'value': eid, 'label': label}
            for eid, label in self._cw.execute(
                'DISTINCT Any C,N ORDERBY N LIMIT %s WHERE C in_scheme S, S eid %%(s)s, '
                'C preferred_label L, L label N, L label ILIKE %%(term)s' % limit,
                {'s': scheme, 'term': u'%%%s%%' % term})]
