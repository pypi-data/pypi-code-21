"""工具."""
from main_conf import PUNCTUATION, PUNCTUATION_ALL, NUMBERS, YISHEN_MIN_PAN,\
    ERSHEN_MIN_PAN, YISHEN_MIN_CAI, ERSHEN_XING_PAN, ERSHEN_CAI
import jieba
from jieba import posseg
import codecs
from dicts import NationalDict, AddressDict
import re

# ABSPATH = os.path.abspath(__file__)
# ABSPATH = os.path.dirname(ABSPATH)+"/"
# 民族
nationalDict = NationalDict("national", "config/national.txt")
# 国家
countryDict = NationalDict("country", "config/country.txt")
# 人民法院
primaryCourtDict = NationalDict("primaryCourt", "config/primary_courts.txt")
# 中级人民法院
middleCourtDict = NationalDict("middleCourt", "config/middle_courts.txt")
# 高级人民法院
advancedCourtDict = NationalDict("advancedCourt", "config/advanced_courts.txt")
# 住所地描述关键词
addressKeyWordDict = NationalDict(
    "address_key_word", "config/address_key_word.txt")
# 省市
cityToProvinceDict = AddressDict("city_province", "config/city_province.txt")
# 省县
townToProvinceDict = AddressDict("town_province", "config/town_province.txt")


def load_dict():
    """载入字典，载入各种各样的字典."""
    DICT = dict()
    DICT["national"] = nationalDict
    DICT["country"] = countryDict
    DICT["primary_court"] = primaryCourtDict
    DICT["middle_court"] = middleCourtDict
    DICT["advanced_court"] = advancedCourtDict
    DICT["address_key_word"] = addressKeyWordDict
    DICT["city_province"] = cityToProvinceDict
    DICT["town_province"] = townToProvinceDict
    for dict_name, dic in DICT.items():
        dic.load_dict()


def seg_words(text):
    """
    分词, 并去掉最后一个标点.

    input : 文本字符串
    output : 词列表
    """
    words = jieba.cut(text, cut_all=False)
    words = [w for w in words]
    index = len(words) - 1
    while index >= 0:
        if words[index] in PUNCTUATION:
            index -= 1
        else:
            break
    words = words[:index + 1]
    return words


def seg_words_with_pos(text):
    """
    带标注分词.

    input : 文本字符串
    output : 词列表
    """
    words = posseg.cut(text)
    words = [w for w in words]
    index = len(words) - 1
    while index >= 0:
        if words[index].word in PUNCTUATION:
            index -= 1
        else:
            break
    words = words[:index + 1]
    return words


def get_next_line(file_path):
    """
    从本地文件获取文本内容的生成器.

    EOF 表示完结
    """
    with codecs.open(file_path, "r", 'GBK') as f:
        while True:
            try:
                line = f.readline()
            except UnicodeDecodeError:
                f = codecs.open(file_path, "r", 'UTF-8')
                line = f.readline()
            if not line:
                yield 'EOF', ""
                break
            raw_line = line
            # line = line.strip()
            line = pre_process(line)
            if not line:
                continue
            yield line, raw_line
            global LINE_COUNT
            LINE_COUNT += 1


def get_next_line2(raw):
    """
    从数据库获得原始文本，生成器.

    EOF 表示完结
    """
    for line in raw.split('\n'):
        if line.strip() == '':
            continue
        raw_line = line
        line = pre_process(line)
        yield line, raw_line
    yield 'EOF', ""


def pre_process(line):
    """
    文本字符串预处理.

    去除空格
    去除全角符号
    """
    line = re.sub(r"[ \u3000\t\s]*", "", line)  # \u3000 审判长\u3000某某
    return line


def startWith(key_words, line):
    """If a line contains one of the word in key_words."""
    tokens = segmentSentence(line)
    if len(tokens) == 0:
        return ''
    for word in key_words:
        if tokens[0].startswith(word):
            return word
    return ''


def segmentSentence(line):
    """."""
    # print "分之前 : ", line
    result = []
    tmp = ""
    flag = 0
    for c in line:
        if c not in PUNCTUATION_ALL or flag == 1:
            if c in ['(', '（']:
                flag = 1
            if c in [')', '）']:
                flag = 0
            tmp += str(c)
        else:
            result.append(tmp)
            tmp = ""
    if len(tmp) > 0:
        result.append(tmp)
    return result


def contains(key_words, line):
    """If a line contains one of the word in key_words."""
    for word in key_words:
        if word in line:
            return True
    return False


def fixname(person):
    """."""
    name = person.name_
    name = re.sub('\(以下简称[^\)]*?\)', '', name)
    name = re.sub('\(组织机构代码[^\)]*?\)', '', name)
    name = re.sub('\(下称[^\)]*?\)', '', name)
    name = re.sub('\(统一社会信用代码[^\)]*?\)', '', name)
    name = re.sub('\(反诉[^\)]*?\)', '', name)
    name = re.sub('[\[\(]原名[^\)]*?[\)\]]', '', name)
    name = re.sub('\(系[^\)]*?经营者\)', '', name)
    name = re.sub('\(系[^\)]*?业主\)', '', name)
    person.name_ = name


def start_with_number(test):
    """."""
    for c in test:
        if c in NUMBERS:
            return True
        return False


def is_address(text):
    """判断一个字符串是否是地址串."""
    text = text.strip()
    if not text:
        return False
    segment_words = posseg.cut(text)
    words = [w for w in segment_words]
    for word in words:
        if word.flag == "ns":
            return True
        else:
            return False
    return False


def add_labels(raw_txt, labels):
    """
    给识别出来的标签增加表示，利于在UI上展示.

    比如标签“法院名称”，会被拓展成：<span id="court">北京市人民法院</span>
    """
    if len(labels) == 0:
        return raw_txt
    label_format = "<span class=\"%s\">%s</span>" % (" ".join(labels), raw_txt)
    return label_format


def rexMatch(pattern, str):
    """正则."""
    p = re.compile(pattern)
    m = p.search(str)
    if m:
        return m
    return []


def rexMatchAll(pattern, str, index):
    """."""
    p = re.compile(pattern)
    m = p.findall(str)
    if m:
        return m[0][index]
    return ""


def rexMatchAll3(pattern, str):
    """."""
    p = re.compile(pattern)
    m = p.findall(str)
    if m:
        for match in m:
            tmp = list(match)
            return "".join(tmp)
    return ""


def rexMatchAll2(pattern, str):
    """."""
    p = re.compile(pattern)
    m = p.findall(str)
    if m:
        result = []
        for match in m:
            tmp = list(match)
            result.append("".join(tmp))
        return result
    return []


def rexMatchAllYiShenAnHao(pattern, str):
    """."""
    p = re.compile(pattern)
    m = p.findall(str)
    if m:
        result = []
        types = []
        for match in m:
            tmp = list(match)
            types.append(tmp[-2:])
            tmp = tmp[0:-2]
            result.append("".join(tmp))
        return result, types
    return [], []


def format_yishen_panjue(case_type, law_type, judge_result):
    """."""
    result = judge_result
    # print '一审结果 : %s' % judge_result
    if case_type == "民事" and "判决" in law_type:
        result = "(部分)支持原告诉讼请求)"
        match = rexMatch(YISHEN_MIN_PAN[0], judge_result)
        if match:
            result = YISHEN_MIN_PAN[1]
    elif case_type == "行政" and "判决" in law_type:
        if "维持" in judge_result:
            result = "维持行政裁决"
        elif "驳回" in judge_result:
            result = "驳回原告诉讼请求"
        elif "撤销" in judge_result:
            result = "撤销行政裁决"
    elif "裁定" in law_type:
        if "移送" in judge_result:
            result = "移送审理"
        elif "终结诉讼" in judge_result:
            result = "终结诉讼"
        elif "转为普通程序" in judge_result:
            result = "转为普通程序"
        else:
            for pattern in YISHEN_MIN_CAI:
                match = rexMatch(pattern[0], judge_result)
                if match:
                    result = pattern[1]
                    break
    return result


def format_ershen_panjue(case_type, law_type, judge_result):
    """."""
    # print '二审结果 : %s' % judge_result
    result = judge_result
    if case_type == "民事" and "判决" in law_type:
        result = "部分维持、部分撤销一审判决"
        for pattern in ERSHEN_MIN_PAN:
            match = rexMatch(pattern[0], judge_result)
            if match:
                result = pattern[1]
                break
    elif case_type == "行政" and "判决" in law_type:
        result = "撤销一审判决"
        for pattern in ERSHEN_XING_PAN:
            match = rexMatch(pattern[0], judge_result)
            if match:
                result = pattern[1]
                break
    elif "裁定" in law_type:
        if "移送" in judge_result:
            result = "移送审理"
        elif "终结诉讼" in judge_result:
            result = "终结诉讼"
        elif "中止诉讼" in judge_result:
            result = "中止诉讼"
        else:
            for pattern in ERSHEN_CAI:
                match = rexMatch(pattern[0], judge_result)
                if match:
                    result = pattern[1]
                    break
    return result


def clean(file_path):
    """文书清理."""
    print('清洗文书:%s' % file_path)
    rawdata = ''
    # with codecs.open(file_path, "r", 'GBK') as f:
    with open(file_path, "r", encoding='GBK') as f:
        try:
            rawdata = f.read()
        except UnicodeDecodeError:
            # f = codecs.open(file_path, "r", 'UTF-8')
            try:
                f = open(file_path, "r")
                rawdata = f.read()
            except UnicodeDecodeError:
                f = open(file_path, "r", encoding='UTF-16')
                rawdata = f.read()
    rawdata = rawdata.strip()
    if rawdata.startswith('<meta'):
        raise Exception("文件格式错误，<meta 开头")

    # 清理北知文书中判决摘要的情况
    rawdata = re.sub('北京知识产权法院(.|\n)*本摘要并非判决之组成部分，不具有法律效力。', '', rawdata)

    rawdata = re.sub(r"[ \u3000\t]*", "", rawdata)
    match = re.findall('书记员.*', rawdata)
    if len(match) > 0:
        rawdata = rawdata[:rawdata.rfind(match[-1]) + len(match[-1])]
    # 清理文书html标签
    regHtml = '["“]?<(html|meta|style|title|h1|h2|h3|h4|h5|link'
    regHtml += '|script|head|body|div).*?>["”]?'
    rawdata = re.sub(regHtml, '', rawdata)
    # 清理空行
    rawdata = re.sub('\n\s*\n', '\n', rawdata)
    # 清理文书首行 法院和判决书在同一行的情况
    rawdataArr = rawdata.split('\n')
    for i in range(len(rawdataArr)):
        if i > 3:
            break
        match = re.search(
            '(.*法 *院).*((行 *政|刑 *事|民 *事).*(判 *决 *书|裁 *定 *书))', rawdataArr[i])
        if match:
            court = match.group(1)
            court = re.sub(' *', '', court)
            txtType = match.group(2)
            txtType = re.sub(' *', '', txtType)
            replace = court + '\n' + txtType
            rawdata = re.sub(
                '(.*法 *院).*((行 *政|刑 *事|民 *事).*(判 *决 *书|裁 *定 *书))',
                replace, rawdata)
            break
    return rawdata


def clean_num(anhao):
    """案号清洗."""
    anhao = anhao.strip()
    anhao = re.sub(
        '(第|字|执|申|初|再|终|恢|保|审|更|特)0+([\d一\-－、\-]+号)', r'\1\2', anhao)
    anhao = re.sub('[（\[【〔]', '(', anhao)
    anhao = re.sub('[）\]】〕]', ')', anhao)
    anhao = re.sub('—+', '-', anhao)
    if not anhao.startswith('('):
        anhao = re.sub('(\d{4})年?(.*)', r'(\1)\2', anhao)
    return anhao
