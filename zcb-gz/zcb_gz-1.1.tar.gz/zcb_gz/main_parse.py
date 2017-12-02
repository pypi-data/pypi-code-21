"""文书解析副程序."""
from .main_tool import seg_words, seg_words_with_pos, contains, \
                        segmentSentence, fixname, rexMatchAllYiShenAnHao, \
                        start_with_number, rexMatch, startWith, clean_num
from .main_conf import ANHAO, PARTIES_BG, PARTIES_DSR, PARTIES_STOP, \
                        LEGAL, PARTIES, RELATIVES, ROLES, \
                        CHINESE_NUM, PARTIES_YG, PROXY, PRINCIPAL, OTHERS, \
                        NATION, POSITION, JUDGE_PATTERN, PATENT_NUMBER, \
                        TRADEMARK_NUMBER, SUMMARY, TRADEMARK_ID, PATENT_ID, \
                        END_JUDGE, YISHENANHAO, FOOTER_YEAR_MONTH_DATE, \
                        FOOTER_ROLE
from .entity import RelativePerson, Person
import re
import copy
import sre_constants
from .ronghui.PatentAndTrademark import patent_review, trademark_review


def process_title(line, law_entity, data_generator):
    """处理文书的title."""
    if '中华人民共和国' == line:
        law_entity.is_foreign_ = True  # 涉外
        line, raw_line = next(data_generator)
    while law_entity.court_ == "":
        if line == "EOF":
            break
        words = seg_words(line)
        for w in words:
            if "法院" in w:
                law_entity.court_ = w
                break
        if law_entity.court_ == "":
            line, raw_line = next(data_generator)
            continue
        # and candidate_court in DICT["advanced_court"].content_:
        if '高级' in law_entity.court_:
            law_entity.court_level_ = '高级'
        # and candidate_court in DICT["middle_court"].content_:
        elif '中级' in law_entity.court_:
            law_entity.court_level_ = '中级'
        else:  # candidate_court in DICT["primary_court"].content_:
            law_entity.court_level_ = '基层'
        match = re.search('.*[省市区]', law_entity.court_)
        if match:
            law_entity.area_ = match.group()
        else:
            tokens = seg_words_with_pos(line)
            address = [token for token in tokens]
            for add in address:
                if add.flag == 'ns':  # 标注为ns的表示是一个地址
                    law_entity.area_ = add.word
                    break
        if "北京高级人民法院" in law_entity.court_:
            law_entity.area_ = "北京"  # hard code。北京市高级人民法院切不开
    return next(data_generator)


def process_type(line, law_entity, data_generator):
    """
    处理文书类型.

    判决书，裁定书
    案件性质
    民事，行政
    """
    line = re.sub(' *', '', line)
    match = re.search('((民事|行政|刑事|执行)(附带民事)?)\w*(裁决书|判决书|裁定书|调解书)', line)
    if match:
        law_entity.nature_ = match.group(1)
        law_entity.type_ = match.group(4)
    else:
        raise Exception('文件不规范，案件类型识别出错')
    return next(data_generator)


def process_number(line, law_entity, data_generator):
    """处理案号,诉讼等级,立案年度."""
    line = line.replace(":", "")
    line = line.replace("：", "")
    match = re.search(ANHAO, line)
    if not match:
        raise Exception('文件不规范，案号识别出错')
    anhao = match.group()
    anhao = clean_num(anhao)
    law_entity.number_ = anhao
    law_entity.year_to_accept_ = match.group(2)
    anhao = re.sub('(.*).{1}', '', anhao)
    level = "再审"
    if re.search('.*(再|抗|监|提|重|申).*', anhao):
        level = "再审"
    elif "终" in line:
        level = "二审"
    elif "初" in line:
        level = "一审"
    law_entity.level_ = level
    return next(data_generator)


def extract_relative_person(line, law_entity, data_generator,
                            relative_person_list):
    """抽取当事人信息."""
    relative_role = ''
    while True:
        if line == "EOF":
            break
        line = line.replace("委托诉讼代理人", "委托代理人").strip()
        line = line.replace("社团法人", "法定代表人").strip()
        if re.search(r'审理终结|审查终结|审理完毕|审查完毕', line):
            break
        if len(line) > 100 and contains(["审理", "不服"], line):
            break
        if contains(["案由", "纠纷"], line):
            break
        if len(line) > 200:
            break
        if relative_role in PARTIES_BG or relative_role in PARTIES_DSR:
            for ps in PARTIES_STOP:
                if line.startswith(ps):
                    break
        p = parsePerson(line, law_entity.level_)
        for n in p.name_.split('、'):
            person = copy.deepcopy(p)
            person.name_ = n
            if person.company_ == 'PRE' or startWith(LEGAL, line):
                try:
                    person.company_ = relative_person_list[relative_role][-1].\
                                        person_.name_
                except Exception as e:
                    person.company_ = ''
            if person.role_ in PARTIES:
                relative_role = person.role_
                person_relative = RelativePerson()
                person_relative.person_ = person
                # relative_person_list = {‘原告’:[]}
                if person.role_ not in relative_person_list:
                    relative_person_list[person.role_] = []
                relative_person_list[person.role_].append(person_relative)
            elif person.role_ in RELATIVES:
                if person.common_:
                    addCommonPersons(
                        relative_person_list, person, relative_role)
                else:
                    relative_person_list[relative_role][-1].relative_.\
                        append(person)
        line, raw_line = next(data_generator)
    return line, raw_line


def addCommonPersons(relative_person_list, person, relative_role):
    """处理共同代理人的情况."""
    common = person.common_
    if relative_role:
        if common == '共同':
            for i in range(len(relative_person_list[relative_role])):
                relative_person_list[relative_role][i].relative_.append(person)
        elif isinstance(common, int):
            for i in range(common):
                if i <= len(relative_person_list[relative_role]):
                    relative_person_list[relative_role][-i].relative_.\
                        append(person)


def parsePerson(text, level):
    """
    获取一个人的相关信息.

    姓名，性别，单位，职务等
    params:
        text, 提取当事人的段落
        level, 诉讼审级
    """
    person = Person()
    text = text.replace(":", "").strip()
    text = text.replace("：", "").strip()
    if len(text) == 0:
        return person
    # 提取曾用名
    match = re.search('曾用名(\w+)', text)
    if match:
        person.usedname_ = match.group(1)
        text = re.sub('曾用名(\w+)', '', text)
    # 被告人xx，xx职务 tokens = ['被告人xx'，'xx职务']
    tokens = segmentSentence(text)
    hasrole = ''
    for sentence_count in range(len(tokens)):
        token = tokens[sentence_count]
        words = seg_words_with_pos(token)
        if len(words) == 0:
            continue
        if sentence_count == 0:
            # 提取当事人身份
            # hasrole = startWith(ROLES, token)
            reg = '|'.join(ROLES)
            # print('(%s)'%reg)
            match = re.search('^(%s)[^、]+' % reg, token)
            if match:
                hasrole = match.group(1)
            else:
                if token in ROLES:
                    hasrole = token
            if not hasrole:
                regCommon = '.*(一|二|两|三|四|五|六|七|八|九|十|十一|十二|十三|十四|十五).*?共同.*?'
                regCommon += '((委托)?(诉讼)?(代表人|代理人))'
                match = re.search(regCommon, token)
                if match:
                    hasrole = match.group(2)
                    person.common_ = CHINESE_NUM.get(match.group(1)) if \
                        CHINESE_NUM.get(match.group(1)) else '共同'
                    token = re.sub(regCommon, '', token)
            if hasrole:
                person.role_ = hasrole
                if person.role_ in PARTIES_YG:
                    person.roleid_ = 1
                    person.identity_ = 1
                elif person.role_ in PARTIES_BG:
                    person.roleid_ = 2
                    person.identity_ = 1
                elif person.role_ in PARTIES_DSR:
                    person.roleid_ = 3
                    person.identity_ = 1
                elif person.role_ in LEGAL:
                    person.identity_ = 2
                elif person.role_ in PROXY:
                    person.identity_ = 3
                elif person.role_ in PRINCIPAL:
                    person.identity_ = 4
                elif person.role_ in OTHERS:
                    person.identity_ = 5
                token = re.sub(hasrole, '', token)
                # 根据审级提取当事人历审身份
                match = re.search(r'[(（](.*?)[）)]', token)
                if match:
                    preRole = match.group(1)
                    bl = pre_role(person, level, preRole)
                    if bl:
                        # print(token)
                        # token = re.sub(r'[(（].*?[）)]', '', token)
                        token = re.sub('[(（]%s[）)]' % preRole, '', token)
                # 除去历审身份后，留下的是当事人名字
                token = re.sub(r'^[(（].*?[）)]', '', token)
                person.name_ = re.sub(r'[(（].*?[）)]$', '', token)
                try:
                    tokens[0] = re.sub(person.name_, '', token)
                except sre_constants.error as e:
                    token = re.sub(r'[(（].*[）)]?', '', token)
                    token = re.sub(r'[(（]?.*[）)]', '', token)
                    token = re.sub(r'[\[].*[\]]?', '', token)
                    person.name_ = token
                    try:
                        repName = person.name_.replace('*', '\*')
                        repName = repName.replace('+', '\+')
                        repName = repName.replace('[', '\[')
                        # print(repName)
                        tokens[0] = re.sub(repName, '', token)
                    except Exception as e:
                        raise e

        # 提取当事人民族，出生时间，性别，职务，所属机构，注册地址，经营地址，住所，其它部分
        if person.role_:
            if not person.nation_:
                match = re.search(NATION, token)
                if match:
                    person.nation_ = match.group()
                    tokens[sentence_count] = ''
            if not person.birth_:
                reg = r'出?生?于?((\w{1,4})年(\w{1,4})月(\w{1,4})日)'
                reg += '(生|出生|$)'
                match = re.search(reg, token)
                if match:
                    person.birth_ = match.group(1)
                    person.b_year_ = match.group(2)
                    person.b_month_ = match.group(3)
                    person.b_day_ = match.group(4)
                    tokens[sentence_count] = ''
            if not person.sex_:
                match = re.search(r'^[男女]$', token)
                if match:
                    person.sex_ = match.group()
                    tokens[sentence_count] = ''
            if not person.title_:
                match = re.search(POSITION, token)
                if match:
                    person.title_ = match.group()
                    # token = re.sub(person.title_, '', token)
                    token = re.sub('(.*)%s' % person.title_, r'\1', token)
                    if re.search('^系?该.*', token) and \
                            person.role_ not in PARTIES:
                        person.company_ = 'PRE'
                    else:
                        if token.startswith('均系'):
                            token = token[2:]
                        elif token.startswith('系'):
                            token = token[1:]
                        person.company_ = token
                    tokens[sentence_count] = ''
            if not person.registered_address_:
                match = re.search(r'^注册地?(.*)', token)
                if match:
                    person.registered_address_ = match.group(1)
                    tokens[sentence_count] = ''
            if not person.address_:
                match = re.search(r'^住址?所?地?(.*)', token)
                if match:
                    person.address_ = match.group(1)
                    tokens[sentence_count] = ''
            if not person.business_address_:
                match = re.search(r'^(经营|营业)(场所|地址|地)?(.*)', token)
                if match:
                    person.business_address_ = match.group(3)
                    tokens[sentence_count] = ''
    # 循环结束
    if not person.name_ and len(tokens) > 1:
        person.name_ = tokens[1]
        tokens[1] = ''
    person.other_ = ''.join(tokens)
    fixname(person)
    # print('-------%s'%person)
    return person


def parse_cause(line, law_entity):
    """提取案由 (案由分段)(区分民事和行政)."""
    if law_entity.cause_:
        return
    # 行政案件类的关键字
    # keyAdministrative = ['纠纷', '一案', '向本院提起', '向本院提出', '向本院申请', '审理终结',
    #    '审查终结', '提起行政诉讼']
    # 民事案件类的关键字
    keyCivil = ['一案', '二案', '三案', '四案', '五案', '六案', '七案', '八案', '九案', '十案',
                '系列案', '两案', '为由', '纠纷']
    if law_entity.nature_ == '行政':
        # for k in keyAdministrative:
        #     index = line.find(k)
        #     if index != -1:
        #         law_entity.cause_ = line[:index+len(k)].strip()
        #         break
        law_entity.cause_ = line[:line.find('。')]
    if law_entity.nature_ == '民事':
        for k in keyCivil:
            m = re.search(r'(.*?)%s' % k, line)
            if m is not None:
                subStr = m.group(1)
                reg = r'(\[.*?\]|【.*?】|\(.*?\)|（.*?）|《.*?》|".*?"|'
                reg += '“.*?”|\'.*?\'|‘.*?’)'
                subStr = re.sub(reg, '', subStr)
                array = subStr.split("。")
                law_entity.cause_ = array[len(array)-1].strip()
                break


def parse_content(
        line, law_entity, data_generator, patentNumber, trademarkNumber):
    """正文分析."""
    parsed_summary = False
    judge_pattern_compiler = re.compile(JUDGE_PATTERN)  # 判决结果正则
    while True:
        if line == "EOF":
            break
        # 抽取专利号
        match = re.search(PATENT_NUMBER, line)
        if match:
            law_entity.patent_number_.add(match.group())
        # 抽取专利复审委的文书号
        law_entity.review_ = law_entity.review_.union(patent_review(line))
        # 抽取商标号
        match = re.search(TRADEMARK_NUMBER, line)
        trademarkTypeDic = {'诉争商标': 1, '引证商标': 2}
        if match:
            trademarkType = match.group(1)
            if not trademarkType:
                reg0 = match.group()
                if '诉争商标' in reg0:
                    trademarkType = '诉争商标'
                elif '引证商标' in reg0:
                    trademarkType = '引证商标'
            law_entity.trademark_number_.add(
                (match.group(2),
                    trademarkTypeDic.get(trademarkType)))
        # 抽取商标评审委的文书号
        law_entity.trademark_review_ = law_entity.trademark_review_.\
            union(trademark_review(line))
        if not parsed_summary and contains(SUMMARY, line):
            parsed_summary = True
            parse_summary(line, law_entity)
        # 判决结果
        match = judge_pattern_compiler.search(line)
        if match:
            line, raw_line = parse_judge_result(
                line, law_entity, data_generator)
        if line.startswith("审判长") or line.startswith("审判员")\
                or line.startswith("代理审判长") or line.startswith("代理审判员"):
            line, raw_line = process_footer(line, law_entity, data_generator)
            break
        line, raw_line = next(data_generator)
    return line, raw_line


def parse_summary(line, law_entity):
    """处理法律文本正文第一段，摘要段."""
    # trademark_id_pattern = "商评字(\(|\[|（|【|〔)(\d+)(\)|\]|）|】|〕)第(\d+)号"
    trademark_id_pattern = TRADEMARK_ID
    # patent_id_pattern = "(专利复审委员会|知识产权局)(.+)第(\d+)号专利"
    patent_id_pattern = PATENT_ID
    sentences = segmentSentence(line)
    for sentence in sentences:
        if law_entity.level_ == "二审" or law_entity.level_ == "再审"\
                or law_entity.level_ == "三审":
            # matches = rexMatchAll2('([\(\[（【〔]?\d+[\)\]】〕）]?)(.{5,30})(\d+)\
            # (号)(之一)?', sentence)
            matches, law_types = rexMatchAllYiShenAnHao(YISHENANHAO, sentence)
            if matches:
                # print 'Sentence2 : %s' % sentence
                # print ",".join(matches)
                law_entity.pre_judge_.extend(matches)
                law_entity.pre_law_type_.extend(law_types)
        if law_entity.nature_ == "行政":
            pattern = re.compile(trademark_id_pattern)
            match = pattern.findall(sentence)
            if match and match[0][0] != "" and match[0][1] != "" \
                    and match[0][2] != "" and match[0][3] != "":
                trademark_id = "商评字%s%s%s第%s号" % (
                    match[0][0], match[0][1], match[0][2], match[0][3])
                law_entity.trademark_id_ = trademark_id
            pattern = re.compile(patent_id_pattern)
            match = pattern.findall(sentence)
            if match and match[0][2] != "":
                patent_id = "第%s号" % (match[0][2])
                law_entity.patent_id_ = patent_id
        # 匹配受理时间和开庭时间
        reg = r'([1-2]\d{3}年(1[0-2]|[1-9])月([1-9]|[1-3][0-9])日)\S*'
        reg += '受理'
        match = re.search(reg, sentence)
        if match:
            receptionTime = match.group(1)
            law_entity.reception_time_ = receptionTime
        reg = r'([1-2]\d{3}年(1[0-2]|[1-9])月([1-9]|[1-3][0-9])日)\S*'
        reg += '开庭'
        match = re.search(reg, sentence)
        if match:
            courtTime = match.group(1)
            law_entity.court_time_ = courtTime


def parse_judge_result(line, law_entity, data_generator):
    """抽取判决结果."""
    # judge_end_indicator = ["提起上诉", "不服", "受理费"]
    judge_end_indicator = END_JUDGE
    judge_result = ""
    while True:
        if line == "EOF":
            break
        sentences = segmentSentence(line)
        for sentence in sentences:
            if contains(judge_end_indicator, sentence):
                break
            judge_result += sentence
        line, raw_line = next(data_generator)
        if not start_with_number(line):
            break
        judge_result += '\n'
    law_entity.judge_results_.append(judge_result)
    return line, raw_line


def process_footer(line, law_entity, data_generator):
    """处理法律文本的落款."""
    while True:
        if line == "EOF":
            break
        if "本件与原本核对无异" == line:
            continue
        # matches = rexMatch('(.+)年(.+)月(.+)日', line)
        matches = rexMatch(FOOTER_YEAR_MONTH_DATE, line)
        if matches:
            law_entity.judge_time_ = matches.group(0)
            line, raw_line = next(data_generator)
            continue
        segment_words = seg_words(line)
        # if len(segment_words) < 2:
        #     break
        person = Person()
        for sw in segment_words:
            if sw in FOOTER_ROLE:
                person.role_ = sw
            elif person.role_:
                person.name_ += sw
        if person.name_:
            if "审判长" in person.role_:
                law_entity.presiding_judge_.append(person)
            elif "审判员" in person.role_:
                law_entity.judges_.append(person)
            elif "人民陪审员" in person.role_:
                law_entity.juror_.append(person)
            elif "法官助理" in person.role_:
                law_entity.judge_assistant_.append(person)
            elif "书记员" in person.role_:
                law_entity.clerk_.append(person)
        line, raw_line = next(data_generator)
    return line, raw_line


def pre_role(person, level, preRole):
    """历审身份."""
    if level == "一审":
        if preRole.find('反诉原告') >= 0:
            person.firrole_ = '反诉原告'
        elif preRole.find('反诉被告') >= 0:
            person.firrole_ = '反诉被告'
        elif preRole.find('反诉第三人') >= 0:
            person.firrole_ = '反诉第三人'
        if person.firrole_:
            return True
    elif level == "二审":
        if preRole.find('原审原告') >= 0 or preRole.find('一审原告') >= 0:
            person.firrole_ = '原告'
        elif preRole.find('原审被告') >= 0 or preRole.find('一审被告') >= 0:
            person.firrole_ = '被告'
        elif preRole.find('原审第三人') >= 0 or preRole.find('一审第三人') >= 0:
            person.firrole_ = '第三人'
        if person.firrole_:
            return True
    elif level == "再审":
        if preRole.find('一审原告') >= 0:
            person.firrole_ = '原告'
        elif preRole.find('一审被告') >= 0:
            person.firrole_ = '被告'
        elif preRole.find('一审第三人') >= 0:
            person.firrole_ = '第三人'
        if preRole.find('原审原告') >= 0 or preRole.find('二审原告') >= 0 \
                or preRole.find('二审上诉人') >= 0:
            person.secrole_ = '上诉人'
        elif preRole.find('原审被告') >= 0 or preRole.find('二审被告') >= 0 \
                or preRole.find('二审被上诉人') >= 0:
            person.secrole_ = '被上诉人'
        elif preRole.find('原审第三人') >= 0 or preRole.find('二审第三人') >= 0:
            person.secrole_ = '第三人'
        if person.firrole_ or person.secrole_:
            return True
    return False
