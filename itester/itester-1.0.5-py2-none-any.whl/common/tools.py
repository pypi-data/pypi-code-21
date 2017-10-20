#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    Meng xiangguo <mxgnene01@gmail.com>
#
#        H A P P Y    H A C K I N G !
#              _____               ______
#     ____====  ]OO|_n_n__][.      |    |]
#    [________]_|__|________)<     |MENG|
#     oo    oo  'oo OOOO-| oo\_   ~o~~~o~'
# +--+--+--+--+--+--+--+--+--+--+--+--+--+
#                        17/6/13  下午5:25

import os
import sys
import glob
import xlrd
import logging

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] - %(process)d - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s')

def fromExcelGetAllCase(fname, method='GET'):
    logging.debug('from %s get all case' % fname)
    bk = xlrd.open_workbook(fname)
    try:
        sh = bk.sheet_by_index(0)
    except:
        logging.error("no sheet in %s named Sheet1" % fname)

    return [tuple(sh.row_values(i)) for i in range(2, sh.nrows) if sh.cell_value(i, 3).upper() == method and sh.cell_value(i, 2).upper() == 'Y']


def testLoader(path, pattern="test_*.xlsx"):
    os.chdir(path)
    return glob.glob(pattern)

def findAllFile(path):
    all_case = []
    for casefile in testLoader(path):
        # 多个case文件进行case 合并
        all_case = all_case + fromExcelGetAllCase(casefile, 'GET') + fromExcelGetAllCase(casefile, 'POST')
    return all_case


def encodeutf8(strname):
    '''对字符串进行处理，始终输出str 类型'''
    if isinstance(strname, unicode):
        strname = strname.encode('utf8')
    elif isinstance(strname, (str, int)):
        strname = strname
    else:
        raise TypeError("value not unicode or str!")

    return strname


def assertDictContains(expect_data, real_data, path='', err_list=[]):
    ''' dict ，list， sting 比对'''
    if isinstance(expect_data, (list, tuple)):
        for index, value in enumerate(expect_data):
            try:
                if not isinstance(value, (list, dict, tuple)):
                    # decode to unicode for diff
                    if isinstance(value, str):
                        value = value.decode('utf-8')

                    if value == real_data[index]:
                        continue
                    else:
                        err_list.append("%s.%s：预期值：%s %s, 实际值：%s %s 对比不一致"
                                        % (encodeutf8(path), str(index), encodeutf8(value), str(type(value)),
                                           encodeutf8(real_data[index]), str(type(real_data[index]))))
                else:
                    err_list = assertDictContains(value, real_data[index], path + '.' + str(index), err_list)
            except Exception, e:
                logging.error(str(e))
    elif isinstance(expect_data, dict):
        for key, value in expect_data.items():
            try:
                if not isinstance(value, (list, dict, tuple)):
                    # decode to unicode for diff
                    if isinstance(value, str):
                        value = value.decode('utf-8')

                    if value == real_data[key]:
                        continue
                    else:
                        err_list.append("%s.%s：预期值：%s %s, 实际值：%s %s 对比不一致"
                                        % (encodeutf8(path), encodeutf8(key), encodeutf8(value), str(type(value)),
                                           encodeutf8(real_data[key]), str(type(real_data[key]))))
                else:
                    err_list = assertDictContains(value, real_data[key], "%s.%s" % (path, key), err_list)
            except Exception as e:
                logging.error(str(e))
    else:
        if not expect_data == real_data:
            err_list.append("预期值：%s %s, 实际值：%s %s 对比不一致" % (expect_data, str(type(expect_data)), real_data, str(type(real_data))))

    return err_list


def prepareStrToDict(strname, ofs='\n'):
    '''
    固定格式的string 转化成 dict

    utoken: 10364121-18687-a133c50e-f3b1-4dd4-967d-b49f034916ae
    key1: values1
    :return {'utoken': '10364121-18687-a133c50e-f3b1-4dd4-967d-b49f034916ae','key1': 'values1'}
    '''
    r_dict = dict()
    if strname:
        for header in strname.split(ofs):
            h = header.split(":")
            r_dict[h[0].strip()] = h[1].strip()

    return r_dict


def prepareRequestsParam(param, ofs='&'):
    '''
    对 requests 的 post 参数进行格式化

    Usage:
        >>> param =  "id=123145&id=123133&aaa=bbb"
        >>> preparePostParam(param)
        (('id', '123145'), ('id', '123133'), ('aaa', 'bbb'))
        >>> param =""
        >>> preparePostParam(param)
        {}
    '''
    if param:
        return tuple([(i.split("=")[0], i.split("=")[1]) for i in param.split(ofs)])
    else:
        return {}

def sendmail(send_to, stmpconf, text='' ,attachment=''):
    import smtplib
    from os.path import basename
    from email.mime.application import MIMEApplication
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.utils import COMMASPACE, formatdate
    from socket import gethostname

    send_from = 'sysadmin@%s' % (gethostname())
    mailtext = """Greetings,

Please see your test report %s .

Thank you!

[%s]
    """ % (text, gethostname() )
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = u'自动化测试报告'

    msg.attach(MIMEText(mailtext))

    if attachment:
        with open(attachment, "rb") as f:
            name = basename(attachment)
            part = MIMEApplication(f.read(), Name=name)
            part['Content-Disposition'] = 'attachment; filename="%s"' % name
            msg.attach(part)

    if sys.platform.startswith('linux'):
        smtp = smtplib.SMTP('127.0.0.1')
    else:
        smtp = smtplib.SMTP()
        smtp.connect(stmpconf[0], 25)
        smtp.login(stmpconf[1], stmpconf[2])

    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()