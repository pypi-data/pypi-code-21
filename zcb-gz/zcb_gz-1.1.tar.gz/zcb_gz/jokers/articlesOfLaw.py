"""."""
import re
import os


def get_law(line):
    """针对单个文书的法条提取，整合进入库的方法."""
    ABSPATH = os.path.abspath(__file__)
    ABSPATH = os.path.dirname(ABSPATH) + "/"
    regList = get_txt(ABSPATH + 'config/article_standardization.txt')
    reList = re.findall(r'((?:\d{4}年)?《.*?》[^。；《]*)', line)
    lawArticle = set()
    for s in reList:
        resub = re.search(r'(?:.*《.*?》.*[条款项目]*)', s)  # 省去了编章节
        if not resub:
            continue
        article = resub.group(0)
        lawTxt = re.search(r"《.*?》", article).group(0)
        lawResp = re.search(r'.*《.*?》', article)
        law = lawResp.group(0)
        articleResp = re.findall(r'第\w*?条', article)
        lawStandar = standardlized(regList, lawTxt)
        if articleResp and lawStandar:
            for item in articleResp:
                itemSub = re.search(r'%s[^条]*[款项目]' % item, article)
                if itemSub:
                    lawStandar = re.sub(
                        r'《.*?》', '《' + lawStandar + '》',
                        law + itemSub.group(0))
                    lawArticle.add(lawStandar)
                else:
                    lawStandar = re.sub(r'《.*?》', '《' + lawStandar + '》', law)
                    lawArticle.add(lawStandar)
        elif lawStandar:
            lawArticle.add(lawStandar)
    return lawArticle


def standardlized(regList, lawTxt):
    """."""
    for regTuple in regList:
        reg = regTuple[0]
        match = re.search(r'%s' % reg, lawTxt)
        if match:
            lawStandar = regTuple[1]
            return lawStandar


def parse_content(id, content):
    """提取文本数据."""
    sContent = re.split(r'\s+本院认为', content)
    returnList = []
    for i in range(len(sContent)):
        dic = {}
        # 编章节条款项目
        reList = re.findall(r'((?:\d{4}年)?《.*?》[^。；《]*)', sContent[i])
        resultList = []
        for s in reList:
            resub = re.search(r'(?:.*[编章节条款项目]+)', s)
            if resub is None:
                resub = re.search(r'.*《.*》', s)
            if resub is not None:
                resultList.append(resub.group(0))
        if resultList is not None and len(resultList) > 0:
            dic['id'] = id
            dic['type'] = i
            dic['articles'] = resultList
            returnList.append(dic)
    return returnList


def parse_record(result):
    """解析结果集."""
    parseResults = []
    for record in result:
        id = record[0]
        content = record[1]
        if content is not None and content != '':
            returnList = parse_content(id, content)
            parseResults.extend(returnList)
    return parseResults


def parseArticle(article):
    """法条分割。例如：《?》第x条，第y条-->《?》第x条  《?》第y条."""
    lawResp = re.search(r'《.*?》', article)
    if lawResp is None:
        return None, None
    law = lawResp.group(0)
    articleResp = re.findall(r'第\w*?条', article)
    if articleResp is None:
        return None, None
    returnList = []
    for item in articleResp:
        itemSub = re.search(r'%s[^条]*[款项目]' % item, article)
        if itemSub is None:
            returnList.append(item)
        else:
            returnList.append(itemSub.group(0))
    return law, returnList


def get_txt(fileName):
    """."""
    txt = open(fileName)
    cList = []
    for line in txt:
        cArray = line.split("——>")
        cTuple = (cArray[0].strip(), cArray[1].strip())
        cList.append(cTuple)
    return cList


def standardizedArticle(article1, article2, regList):
    """标准化法条."""
    for regTuple in regList:
        reg = regTuple[0]
        match = re.search(r'%s' % reg, article2)
        if match is not None:
            article3 = regTuple[1]
            article3 = re.sub(r'《.*?》', '《' + article3 + '》', article1)
            return article3
    return None


def extractLaw(article):
    """提取书名号内的内容."""
    law = ''
    if article is not None:
        law = re.search(r"《.*?》", article).group(0)
    return law


def extract_detail(content):
    """."""
    law = re.search('《(.*?)》', content)
    if law:
        law = law.group(1)
        article = re.search('》\)?）?第?(.*?)条', content)
        if article:
            article = article.group(1)
            content = re.sub('》\)?）?第?(.*?)条', '》', content)
        paragraph = re.search('》第?(.*?)款', content)
        if paragraph:
            paragraph = paragraph.group(1)
            content = re.sub('》第?(.*?)款', '》', content)
        item = re.search('》第?(.*?)项', content)
        if item:
            item = item.group(1)
        return law, converter(article), converter(paragraph), converter(item)
    else:
        return None, None, None, None


def converter(number):
    """."""
    if not number:
        return ''
    number = re.sub(r'\(|（|\)|）', '', number)
    if len(number) < 1:
        return ''
    if number.isdigit():
        return number
    dic = {
            '零': '0', '一': '1', '二': '2', '三': '3', '四': '4',
            '五': '5', '六': '6', '七': '7', '八': '8', '九': '9',
            '十': '10', '百': '100'}
    dnum = ''
    if number[0] == '十':
        number = '一' + number
    if number[len(number) - 1] == '十':
        number = number + '零'
    if number[len(number) - 1] == '百':
        number = number + '零' + '零'
    for d in number:
        if d not in dic.keys():
            return None
        if d != '百' and d != '十':
            dnum = dnum + dic.get(d)
    return dnum
