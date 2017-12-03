# -*- coding: utf-8 -*-

{
    'name': '{{ addon_name }}',
    'version': '{{ addon_version }}',
    'category': '{{ addon_category }}',
    'sequence': 75,
    'summary': '{{ addon_summary }}',
    'author': '{{ user_name }}{% if user_company %}, ({{ user_company }}){% endif %}',
    'website': '{{ user_website }}',
    'images': [],
    'description': """
{{ addon_name }}
{{ addon_name_len * '=' }}
{{ addon_description }}
        """,
    'depends': {{ addon_depends }},
    'data': [],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
