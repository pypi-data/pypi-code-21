  # -*- coding: utf-8 -*-
"""
Created on Tue May  9 14:33:18 2017

@author: Administrator
"""
import re

# 返回专利复审委决定号
def patent_review(line):
    reViewSet = set()
    match = re.findall("(第|作出的)([0-9]+)(号)\w*(无效宣告|无效决定|复审请求)",line)
    for m in match:
        reView = m[1]
        if '无效' in m[3]:
            judgeType = '无效'
        elif '复审' in m[3]:
            judgeType = '复审'
        reViewSet.add((reView, judgeType))
    return reViewSet

# 返回商标评审委文书号
def trademark_review(line):
    reViewSet = set()
    match = re.findall("(商评字)([^\r\n\t。；:；:号第]{,6}[\r\n\t]{,1}[第]{,1}[^0-9。；:]{,3})([0-9０－９]+)(号)?",line)
    for m in match:
        reViewSet.add("".join(m))
    return reViewSet
