# -*- coding: utf-8 -*-

'''
Created on 2014-5-18
@author: linkeddt.com
'''

from __future__ import unicode_literals

from django.views.generic import TemplateView


class IframeView(TemplateView):
    template_name = "Admin/iframe.htm"

    def get(self, request, *args, **kwargs):
        context = super(IframeView, self).get_context_data(**kwargs)
        query = self.request.GET.copy()
        url = query.get('url', '')
        context['page_url'] = url
        return self.render_to_response(context)
