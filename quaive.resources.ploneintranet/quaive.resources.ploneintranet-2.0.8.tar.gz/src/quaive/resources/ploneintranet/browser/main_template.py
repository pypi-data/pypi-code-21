# coding=utf-8
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.browser.main_template import MainTemplate as BaseMainTemplate  # noqa


class MainTemplate(BaseMainTemplate):
    main_template = ViewPageTemplateFile('templates/main_template.pt')
    ajax_template = main_template
