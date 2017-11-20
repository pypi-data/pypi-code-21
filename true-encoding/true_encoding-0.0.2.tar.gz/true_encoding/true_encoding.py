# coding:utf-8
# author:UlionTse

import re


def Tcode(response):
    '''
    Solve the problem of 'ISO-8859-1'.
    :param response:
    :return:
    '''
    if 'charset="' in response.text:
        pattern = re.compile('charset="(.*?)"',re.S)
        return re.findall(pattern,response.text)[0]

    elif ('charset=gb2312' or 'charset=GB2312') in response.text:
        return 'GB2312'

    elif ('charset=gbk' or 'charset=GBK') in response.text:
        return 'gbk'

    elif ('charset=cp936' or 'charset=CP936') in response.text:
        return 'cp936'

    elif ('charset=ascii' or 'charset=ASCII') in response.text:
        return 'ASCII'
    else:
        return 'utf-8'

