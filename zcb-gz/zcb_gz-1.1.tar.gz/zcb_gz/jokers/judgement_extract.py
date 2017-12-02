"""在判决结果截断的基础上对判决结果进行提取."""
import re


class Judgement(object):
    """docstring for ."""

    def __init__(self):
        """."""
        self.ANHAO = "(撤销|维持|变更).*([\(\[（【〔（]\d{4}[\)\]】〕）]"
        self.ANHAO += "\w+(初|终)\w+[\d、\-—]+号).*(判决|裁定)"
        self.regRuleFirCivil = []
        self.regRuleFirAdmini = []
        self.regRuleFirCriminal = []
        self.regRuleSecCivil = []
        self.regRuleSecAdmini = []
        self.regRuleSecCriminal = []
        self.regRuleReCivil = []
        self.regRuleReAdmini = []
        self.regRuleReCriminal = []
        self.regJudgeFirCivil = []        # 民事一审判定书
        self.regJudgeFirAdmini = []       # 行政一审判定书
        self.regJudgeFirCriminal = []     # 刑事一审判定书
        self.regJudgeSecCivil = []        # 民事二审判定书
        self.regJudgeSecAdmini = []       # 行政二审判定书
        self.regJudgeSecCriminal = []     # 刑事二审判定书
        self.regJudgeReCivil = []         # 民事再审判定书
        self.regJudgeReAdmini = []        # 行政再审判定书
        self.regJudgeReCriminal = []      # 刑事再审判定书

    def generate_judgement_cd(self, law_entity, level, item):
        """裁定书."""
        offen, denfen = self.parse_rule(law_entity, item, level)
        return offen, denfen

    def generate_judgement_pj(self, law_entity, level, results):
        """判决书."""
        offen, denfen = self.parse_judge(law_entity, results, level)
        return offen, denfen

    def parse_rule(self, law_entity, line, resulttype):
        """裁定书的判决结果提取."""
        offen = 0
        denfen = 0
        regRule = []
        if law_entity.level_ == '一审' and law_entity.nature_ == '民事':
            regRule = self.regRuleFirCivil
        elif law_entity.level_ == '一审' and law_entity.nature_ == '行政':
            regRule = self.regRuleFirAdmini
        elif law_entity.level_ == '一审' and law_entity.nature_ == '刑事':
            regRule = self.regRuleFirCriminal
        elif law_entity.level_ == '二审' and law_entity.nature_ == '民事':
            regRule = self.regRuleSecCivil
        elif law_entity.level_ == '二审' and law_entity.nature_ == '行政':
            regRule = self.regRuleSecAdmini
        elif law_entity.level_ == '二审' and law_entity.nature_ == '刑事':
            regRule = self.regRuleSecCriminal
        elif law_entity.level_ == '再审' and law_entity.nature_ == '民事':
            regRule = self.regRuleReCivil
        elif law_entity.level_ == '再审' and law_entity.nature_ == '行政':
            regRule = self.regRuleReAdmini
        elif law_entity.level_ == '再审' and law_entity.nature_ == '刑事':
            regRule = self.regRuleReCriminal
        if line.find('反诉') >= 0 and law_entity.nature_ == '民事'\
                and law_entity.level_ == '一审':
            return -1, -1
        for reg in regRule:
            if reg[3] == resulttype and re.search(reg[0], line):
                offen = reg[1]
                denfen = reg[2]
                break
        return offen, denfen

    def parse_judge(self, law_entity, results, resulttype):
        """判决书的判决结果提取."""
        offen = 0
        denfen = 0
        regList = []
        if law_entity.level_ == '一审' and law_entity.nature_ == '民事':
            regList = self.regJudgeFirCivil
        elif law_entity.level_ == '一审' and law_entity.nature_ == '行政':
            regList = self.regJudgeFirAdmini
        elif law_entity.level_ == '一审' and law_entity.nature_ == '刑事':
            regList = self.regJudgeFirCriminal
        elif law_entity.level_ == '二审' and law_entity.nature_ == '民事':
            regList = self.regJudgeSecCivil
        elif law_entity.level_ == '二审' and law_entity.nature_ == '行政':
            regList = self.regJudgeSecAdmini
        elif law_entity.level_ == '二审' and law_entity.nature_ == '刑事':
            regList = self.regJudgeSecCriminal
        elif law_entity.level_ == '再审' and law_entity.nature_ == '民事':
            regList = self.regJudgeReCivil
        elif law_entity.level_ == '再审' and law_entity.nature_ == '行政':
            regList = self.regJudgeReAdmini
        elif law_entity.level_ == '再审' and law_entity.nature_ == '刑事':
            regList = self.regJudgeReCriminal
        for line in results:
            if line.find('反诉') >= 0 and law_entity.nature_ == '民事'\
                    and law_entity.level_ == '一审':
                return -1, -1
            for reg in regList:
                if reg[3] == resulttype and re.search(reg[0], line):
                    if reg[1]:
                        offen = 1
                    if reg[2]:
                        denfen = 1
                    break
        return offen, denfen

    def parse_pre(self, judge, txt):
        """提取历审案号和判决结果以及文书类型."""
        if judge.trial_level_ == '二审':
            match = re.search(self.ANHAO, txt)
            if match:
                judge.firjudgement_ = match.group(1)
                judge.fircasenum_ = match.group(2)
                judge.firitype_ = match.group(4)
        elif judge.trial_level_ == '再审':
            print(re.findall(self.ANHAO, txt))
            for match in re.findall(self.ANHAO, txt):
                if "终" in match[2]:
                    judge.secjudgement_ = match[0]
                    judge.seccasenum_ = match[1]
                    judge.secitype_ = match[3]
                elif "初" in match[2]:
                    judge.firjudgement_ = match[0]
                    judge.fircasenum_ = match[1]
                    judge.firitype_ = match[3]

    def parse_administrative(self, judge, txt):
        """解析行政文书号和判决结果."""
        match = re.search(
            '[0-9]*号?.*((重新)(作出)?.*(争议|复审|无效)?.*(决定|裁定|申请))', txt)
        if match:
            judge.administrative_judgement_ = match.group(2)
            judge.administrative_ = re.sub(match.group(2), '', match.group(1))
            return
        match = re.search(
            '(重新|维持|撤销|变更).*?((商评字|[\[〔［][0-9]{4}[］〕\]]|第?[0-9]+号?)\
            .*(争议|无效|无效宣告|驳回复审|复审|审查|争议).*(决定|裁定|申请|裁定)书?》?)', txt)
        if match:
            judge.administrative_judgement_ = match.group(1)
            judge.administrative_ = match.group(2)
            return
        match = re.search(
            '([0-9]*\.[0-9xX].*(无效|争议|复审).*(决定|裁定|申请)).*((重新)(作出)?)', txt)
        if match:
            judge.administrative_judgement_ = match.group(5)
            judge.administrative_ = match.group(1)
            return
