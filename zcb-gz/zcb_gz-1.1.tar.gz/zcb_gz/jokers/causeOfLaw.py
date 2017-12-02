"""案由."""
import pymysql
import re
import os
import sys


def getTxt(path):
    """民事案由标准化文件."""
    txt = open(path)
    cList = []
    for line in txt:
        cArray = line.split("——>")
        cTuple = (cArray[0].strip(), cArray[1].strip())
        cList.append(cTuple)
    return cList


def truncate(content):
    """
    民事文书.

    对原始文书截断
    （一案|二案|三案|四案|五案|六案|七案|八案|九案|十案|纠纷）从前到后优先级查找
    去掉之前的中文字符集【】,[],（）,(),《》,“”,"",'‘,’'之间的内容
    截取一案之前的整句
    """
    keywords = ['一案', '二案', '三案', '四案', '五案', '六案', '七案', '八案', '九案', '十案',
                '系列案', '两案', '为由', '纠纷']
    m = None
    match = re.search('案由[:：](.*)', content)
    if match:
        return match.group(1).strip()
    for key in keywords:
        m = re.search(r'(.*?)%s' % key, content)
        if m is not None:
            break
    if m is None:
        return ''
    subStr = m.group(1)
    if key == '纠纷':
        subStr = subStr + '纠纷'
    subStr = re.sub(
        r'(\[.*?\]|【.*?】|\(.*?\)|（.*?）|《.*?》|".*?"|“.*?”|\'.*?\'|‘.*?’)',
        '', subStr)
    array = subStr.split("。")
    return array[len(array) - 1].strip()


def clean(coastr, results):
    """."""
    for par in results:
        if par:
            par = par.replace('(', '\(')
            par = par.replace(')', '\)')
            par = par.replace('*', '\*')
            par = par.replace('+', '\+')
            par = par.replace('[', '\[')
            par = par.replace(']', '\]')
            try:
                coastr = re.sub('.*%s' % par, '', coastr)
            except Exception as e:
                print('par:%s,coastr:%s' % (par, coastr))
                raise
    return coastr


def standardized(cause):
    """
    民事文书.

    标准化
    t_add_case_anyou表,anyou2字段是经过清洗后的字段，使用该字段匹配关键词确定案由
    return:['案由1','案由2'...]
    """
    ABSPATH = os.path.dirname(os.path.abspath(sys.argv[0]))
    regList = getTxt(ABSPATH + "/config/cause_standardization.txt")
    returnList = []
    if cause is None or cause == '':
        return returnList
    arr = []
    if re.search('著作权(权属)?(、|和|及)(权属)?侵权(纠纷)?', cause):
        arr.append(cause)
    else:
        arr = re.split('、|和|及', cause)
    for sa in arr:
        anyou = None
        for regTuple in regList:
            reg = regTuple[0]
            match = re.search(r'%s' % reg, sa)
            if match is not None:
                anyou = regTuple[1]
                break
        if anyou is not None:
            returnList.append(anyou)
    if len(returnList) <= 1:
        return ''.join(returnList)
    return returnList


def truncate_administrative(line):
    """行政文书 案由截断."""
    key = ['纠纷', '一案', '向本院提起', '向本院提出', '向本院申请', '审理终结', '审查终结', '提起行政诉讼']
    locate = ['商标([\u4e00-\u9fa5]+)行政', '商标([\u4e00-\u9fa5]+)裁定',
              '商标([\u4e00-\u9fa5]+)决定', '专利权?([\u4e00-\u9fa5]+)行政',
              '专利权?([\u4e00-\u9fa5]+)裁定',
              '专利权?([\u4e00-\u9fa5]+)决定']
    if not line:
        return ''
    for k in key:
        index = line.find(k)
        if index != -1:
            cause = line[:index + len(k)]
            cause = cause.strip()
            for l in locate:
                match = re.search(l, cause)
                if match:
                    return match.group(1)
            return cause
    return ''


reg_administrative = {'驳回': '驳回复审', '无效': '无效宣告', '异议': '异议复审', '争议': '争议',
                      '撤销复审': '撤销复审',
                      '专利(权)?(申请)?(复审)?(行政)?(确权)?(纠纷|诉讼)': '其他专利行政授权确权纠纷',
                      '(其他|因)?商标(行政)?纠纷': '其他商标行政授权确权纠纷',
                      '商标.*转让(申请)?': '其他商标行政授权确权纠纷',
                      '行政处罚': '行政处罚', '商标.*核准转让': '其他商标授权确权纠纷',
                      '商标申请不予核准': '不予注册复审',
                      '商标撤销行政纠纷': '撤销复审', '商标不予注册复审行政纠纷': '不予注册复审'}


def standardized_administrative(cause):
    """行政文书 案由标准化."""
    if not cause:
        return ''
    for r in reg_administrative:
        if re.search(r, cause):
            return reg_administrative.get(r)
    return ''


def truncate_crime(line):
    """刑事文书,案由截断."""
    reg = '.*(一案|审查终结|审理终结|审理完毕|组成合议庭|本院受理后|向本院提起公诉)'
    match = re.search(reg, line)
    if match:
        return match.group()
    return ''


def standardized_crime(cause):
    """刑事文书,案由标准化."""
    ABSPATH = os.path.dirname(os.path.abspath(sys.argv[0]))
    regList = getTxt(ABSPATH + "/config/cause_crime_standardization.txt")
    for regTuple in regList:
        reg = regTuple[0]
        match = re.search(r'%s' % reg, cause)
        if match is not None:
            return regTuple[1]
    return ''


def truncate_main(nature, line):
    """."""
    cause = ''
    if nature == '民事' or nature == '行政':
        cause = truncate(line)
    # if nature == '行政':
    #     cause = truncate_administrative(line)
    if nature == '刑事':
        cause = truncate_crime(line)
    return cause


def standardized_main(nature, cause):
    """."""
    anyou = ''
    if nature == '民事':
        anyou = standardized(cause)
    if nature == '行政':
        anyou = standardized_administrative(cause)
    if nature == '刑事':
        anyou = standardized_crime(cause)
    return anyou


def administrative_cause():
    """行政案件，根据当事人区分商标和专利的无效宣告、驳回复审区分，需要整合进案由标准化的代码."""
    sql = '''SELECT id, caseid, anyou from ip_infos.t_case_coa_relations
        where id>%s and (anyou = '无效宣告' or anyou = '驳回复审')
        order by id limit 1000'''
    sqlParties = '''SELECT name from ip_infos.t_case_parties
        where identity = 1 and caseid = %s'''
    sqlUpdate = '''UPDATE ip_infos.t_case_coa_relations set anyou = %s
        where id = %s'''
    conn = pymysql.connect(host="rm-2ze0ek7c57w65y4t6o.mysql.rds.aliyuncs.com",
                           user="ip_infos_root", passwd="zcb!1511",
                           charset="utf8")
    cur = conn.cursor()
    pageNum = 0
    while True:
        print(pageNum)
        cur.execute(sql, pageNum)
        results = cur.fetchall()
        if len(results) == 0:
            break
        for record in results:
            id = record[0]
            pageNum = id
            caseid = record[1]
            anyou = record[2]
            cur.execute(sqlParties, caseid)
            print(id)
            for r in cur.fetchall():
                if re.search('专利局|国家知识产权局|知识产权局|专利评审委员会|专利复审委员会', r[0]):
                    cur.execute(sqlUpdate, (anyou + "(专利)", id))
                    print('%s,%s' % (caseid, anyou + "(专利)"))
                    break
                elif re.search('商标局|商标复审委员会|商标评审委员会', r[0]):
                    cur.execute(sqlUpdate, (anyou + "(商标)", id))
                    print('%s,%s' % (caseid, anyou + "(商标)"))
                    break
        conn.commit()


if __name__ == '__main__':
    administrative_cause()
