# -*- coding:utf-8 -*-
from django.dispatch import receiver
from django.db.models.signals import post_save
from . import models, helper, choices
import logging

log = logging.getLogger("django")


@receiver(post_save, sender=models.School)
def init_grade(sender, **kwargs):
    try:
        school = kwargs['instance']
        if school.grades.count() == 0:
            helper.gen_default_grades(school)
    except Exception, e:
        log.error("init_grade error: %s" % e)


@receiver(post_save, sender=models.Grade)
def init_session(sender, **kwargs):
    try:
        grade = kwargs['instance']
        school = grade.school
        helper.gen_default_session(school, grade.number-1)
    except Exception, e:
        log.error("init_session error: %s" % e)
