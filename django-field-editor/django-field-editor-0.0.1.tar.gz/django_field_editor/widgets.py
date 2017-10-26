# -*- coding: utf-8 -*-

import json

from django.forms import Widget, Media


class JsonEditorWidget(Widget):
    """在 django  admin 后台中使用  jsoneditor 处理 JSONField"""

    template_name = 'json_editor.html'

    # 配置
    mode = 'tree'

    # 展开
    expand_all = True

    def __init__(self, attrs=None):
        super(JsonEditorWidget, self).__init__(attrs)

    @property
    def media(self):
        css = {
            "all": ["json_widget/jsoneditor.min.css"]
        }
        js = ["json_widget/jsoneditor-minimalist.min.js"]

        return Media(js=js, css=css)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['mode'] = self.mode
        context['widget']['expand_all'] = self.expand_all
        return context

    def render(self, name, value, attrs=None, renderer=None):

        if isinstance(value, str):
            try:
                value = json.loads(value)
            except Exception:
                value = {}
        return super().render(name, json.dumps(value))
