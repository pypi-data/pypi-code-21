#coding:utf-8
'''
* coder  : Dzlua
* email  : 505544956@qq.com
* module : api-cli
* path   : api_cli/utils
* file   : templete.py
* time   : 2017/10/30
'''
#--------------------#
_content = """
* coder  : {coder}
* email  : {email}
* module : {module}
* path   : {path}
* file   : {file}
* time   : {time}
"""
#--------------------#

#--------------------#
_py = """{#}coding:utf-8
'''""" + _content + """'''
{#}--------------------{#}
"""
#----------#
_cc = '/**' + _content + '*/'
#----------#
_php = """<?php
""" + _cc + """

?>"""
#----------#
_html = '<!--' + _content + '-->'
#----------#
_lua = '--[[' + _content + '--]]'
#--------------------#

#--------------------#
header = {
    'py': _py,
    'c': _cc,
    'c++': _cc,
    'css': _cc,
    'js': _cc,
    'html': _html,
    'vue': _html,
    'php': _php,
    'lua': _lua,
}
#--------------------#
