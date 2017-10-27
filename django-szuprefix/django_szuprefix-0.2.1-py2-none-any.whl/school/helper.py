# -*- coding:utf-8 -*-
import datetime

__author__ = 'denishuang'
from django_szuprefix.utils import dateutils
from . import choices
import re

def gen_default_grades(school):
    gs = choices.MAP_SCHOOL_TYPE_GRADES.get(school.type)
    if not gs:
        return
    for number, name in gs:
        school.grades.create(name=name, number=number)


def gen_default_session(school, offset=0):
    today = dateutils.format_the_date()
    year = today.month >= 8 and today.year or today.year - 1
    year -= offset
    return school.sessions.get_or_create(
        number=year,
        defaults=dict(
            name=u"%s届" % year,
            begin_date="%s-09-01" % year,
            end_date="%s-07-01" % (year + 1))
    )



RE_GRADE = re.compile(ur"(\d+)[级]*")


def grade_name_to_number(grade_name):
    m = RE_GRADE.search(grade_name)
    if m:
        no = int(m.group(1))
        if no < 50:
            no += 2000
        elif no < 100:
            no += 1900
        return no


def cur_grade_number(grade_name, today=None):
    """
     when today is 2016.9.10

     cur_grade_number(u"14级")
     3
     cur_grade_number(u"2015级")
     2
     cur_grade_number(u"2016级")
     1
     cur_grade_number(u"98级")
     19
     cur_grade_number(u"17级")
     0
     cur_grade_number(u"18级")
     -1
    """
    gno = grade_name_to_number(grade_name)
    if not gno:
        return
    today = today or datetime.date.today()
    num = today.year - gno
    if today.month >= 8:
        num += 1
    return num

def cur_grade_year(grade_num, today=None):
    today = today or datetime.date.today()
    year = today.year - grade_num
    if today.month >= 8:
        year += 1
    return year

def cur_grade_name(grade_num, today=None):
    return u"%s级" % cur_grade_year(grade_num, today)

def get_cur_term(corp):
    from ..utils.dateutils import format_the_date
    today = format_the_date()
    year = today.month >= 8 and today.year or today.year - 1
    month = today.month
    day = today.day
    part = (month*100+day<215  or month >=8 ) and 1 or 2
    name = "%s-%s学年第%s学期" % (year, year+1, part == 1 and "一" or "二")
    start_date=datetime.date(today.year, part==1 and 9 or 3, 1)
    term, created = corp.school_terms.get_or_create(year=year,
                                    part = part,
                                    defaults = dict(name=name,
                                                   start_date=start_date))
    return term
