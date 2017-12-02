"""."""


class Person:
    """."""

    def __init__(self):
        """."""
        self.name_ = ""  # 姓名
        self.usedname_ = ""  # 曾用名
        self.role_ = ""  # 身份
        self.roleid_ = ""  # 1.原告 2.被告 3.第三人
        self.identity_ = ""  # 身份 1.当事人 2.法定代表人 3.诉讼代表人 4.授权代表人 5.其它
        self.firrole_ = ""  # 一审身份
        self.secrole_ = ""  # 二审身份
        self.nation_ = ""  # 民族
        self.sex_ = ""  # 性别
        self.birth_ = ""  # 出生日期
        self.b_year_ = ""
        self.b_month_ = ""
        self.b_day_ = ""
        self.address_ = ""  # 住所地址
        self.registered_address_ = ""  # 注册地址
        self.business_address_ = ""  # 经营地址
        self.country_ = ""  # 国籍
        self.company_ = ""  # 公司
        self.title_ = ""  # 职务
        self.other_ = ""  # 其它
        self.common_ = ''  # 共同代理人（1-10|共同）

    def __repr__(self):
        """."""
        return '%s,%s,%s' % (self.role_, self.name_, self.birth_)

    def to_csv(self):
        """."""
        tmp = [
                "name=%s" % self.name_, "sexy=%s" % self.sex_,
                "birth=%s" % self.birth_, "address=%s" %
                self.address_, "country=%s" % self.country_,
                "company=%s" % self.company_, "job_title=%s" % self.title_]
        return ",".join(tmp)

    def to_list(self):
        """."""
        member_list = [self.name_, self.sex_, self.birth_,
                       self.address_, self.country_,
                       self.company_, self.title_]
        return member_list


class RelativePerson:
    """."""

    def __init__(self):
        """."""
        self.person_ = Person()
        self.proxy_ = []
        self.legal_representative_ = []
        self.relative_ = []  # 新版，代理人和法人放在一起
        self.previous_id_ = ""

    def __repr__(self):
        """."""
        return '<当事人 % r>' % self.person_.name_ + '\n' \
            '<代理人 % r>' % self.proxy_ + '\n' \
            '<法人代表 % r>' % self.legal_representative_

    def to_csv(self):
        """."""
        tmp = [self.person_.name_, self.person_.address_,
               self.person_.country_]  # 当事人个人信息，名字，地址，国籍
        for p in self.legal_representative_:
            tmp.append(p.name_)
        for p in self.proxy_:
            tmp.append(p.name_)
            tmp.append(p.company_)
            tmp.append(p.title_)
        return "-".join(tmp)


class LawEntity:
    """."""

    def __init__(self):
        """."""
        self.id_ = "-1"
        self.title_ = ''  # 文书标题
        self.court_ = ""  # 审理法院
        self.court_level_ = ""  # 法院级别
        self.area_ = ""  # 案件地区
        self.is_foreign_ = False
        self.year_to_accept_ = None  # 立案年度
        self.type_ = ""  # 文书类型
        self.nature_ = ""  # 案件性质
        self.number_ = ""  # 案件号
        self.start_time_ = ""  # 案件开始时间
        self.level_ = ""  # 诉讼等级
        self.parent_ = ""  # 上一级诉讼号
        self.judge_time_ = ""  # 判决时间
        self.judge_results_ = []  # 判决结果
        self.reception_time_ = ''  # 受理时间
        self.court_time_ = ''  # 开庭时间
        self.trademark_id_ = ""  # 商标号
        self.patent_id_ = ""  # 专利号
        self.yuangao_ = []  # 原告
        self.beigao_ = []  # 被告
        self.third_people_ = []  # 第三人
        self.party_ = []  # 新版，集合原告，被告和第三人
        self.presiding_judge_ = []  # 审判长
        self.judges_ = []  # 审判员
        self.juror_ = []  # 陪审员
        self.clerk_ = []  # 书记员
        self.judge_assistant_ = []  # 法官助理
        self.pre_judge_ = []
        self.pre_law_type_ = []
        self.next_judge_ = []
        self.cause_ = ""  # 案由
        self.law_ = set()  # 法条
        self.patent_number_ = set()  # 专利号
        self.review_ = set()  # 专利复审
        self.trademark_number_ = set()  # 商标号
        self.trademark_review_ = set()  # 商标评审
        self.appeal_money_ = ''
        self.judge_money_ = ''
        self.accuser_ = ''
        self.Judement_ = ''

    def __repr__(self):
        """."""
        yuangao = []
        yuangao_rep = []
        yuangao_proxy = []
        for yg in self.yuangao_:
            yuangao.append(yg.person_.name_)
            for rep in yg.legal_representative_:
                yuangao_rep.append(rep.name_)
            for proxy in yg.proxy_:
                yuangao_proxy.append(proxy.name_)
        beigao = []
        beigao_rep = []
        beigao_proxy = []
        for bg in self.beigao_:
            beigao.append(bg.person_.name_)
            for rep in bg.legal_representative_:
                beigao_rep.append(rep.name_)
            for proxy in bg.proxy_:
                beigao_proxy.append(proxy.name_)
        third_people = []
        third_people_rep = []
        third_people_proxy = []
        for tp in self.third_people_:
            third_people.append(tp.person_.name_)
            for rep in tp.legal_representative_:
                third_people_rep.append(rep.name_)
            for proxy in tp.proxy_:
                third_people_proxy.append(proxy.name_)
        presiding_judge = []
        for pj in self.presiding_judge_:
            presiding_judge.append(pj.name_)
        judges = []
        for jud in self.judges_:
            judges.append(jud.name_)
        juror = []
        for jur in self.juror_:
            juror.append(jur.name_)
        clerk = []
        for cle in self.clerk_:
            juror.append(cle.name_)
        judge_assistant = []
        for ja in self.judge_assistant_:
            judge_assistant.append(ja.name_)
        return '<文书标题 % r>' % self.title_ + '\n' \
            '<审理法院 % r>' % self.court_ + '\n' \
            '<法院级别 % r>' % self.court_level_ + '\n' \
            '<案件地区 % r>' % self.area_ + '\n' \
            '<是否涉外 % r>' % self.is_foreign_ + '\n' \
            '<立案年度 % r>' % self.year_to_accept_ + '\n' \
            '<文书类型 % r>' % self.type_ + '\n' \
            '<案件性质 % r>' % self.nature_ + '\n' \
            '<案件号 % r>' % self.number_ + '\n' \
            '<案件开始时间 % r>' % self.start_time_ + '\n' \
            '<诉讼等级 % r>' % self.level_ + '\n' \
            '<上一级诉讼号 % r>' % self.parent_ + '\n' \
            '<判决时间 % r>' % self.judge_time_ + '\n' \
            '<判决结果 % r>' % self.judge_results_ + '\n' \
            '<受理时间 % r>' % self.reception_time_ + '\n' \
            '<开庭时间 % r>' % self.court_time_ + '\n' \
            '<商标号: % r>' % self.trademark_id_ + '\n' \
            '<专利号 % r>' % self.patent_id_ + '\n' \
            '<审判长 % r>' % presiding_judge + '\n' \
            '<审判员 % r>' % judges + '\n' \
            '<陪审员 % r>' % juror + '\n' \
            '<书记员 % r>' % clerk + '\n' \
            '<法官助理 % r>' % judge_assistant + '\n' \
            '<案由 %r>' % self.cause_ + '\n' \
            '<前一级案号 %r>' % self.pre_judge_ + '\n' \
            '<前一级类型 %r>' % self.pre_law_type_ + '\n' \
            '<法条 %r>' % self.law_ + '\n' \
            '<专利号 %r>' % self.patent_number_ + '\n' \
            '<专利复审文书号 %r>' % self.review_ + '\n' \
            '<商标号 %r>' % self.trademark_number_ + '\n' \
            '<商标评审文书号 %r>' % self.trademark_review_

    def to_csv(self):
        """."""
        tmp = []
        tmp.append(self.id_)  # 文书id 0
        tmp.append(self.number_)  # 案件号 1
        tmp.append(self.court_)  # 法院名称 2
        tmp.append(self.court_level_)  # 法院级别3
        tmp.append(self.area_)  # 案件地区4
        tmp.append(self.nature_)  # 案件性质5， 行政、民事
        tmp.append(self.type_)  # 文书类型6，	判决书、调解书
        tmp.append(self.year_to_accept_)  # 案件时间7

        tmp.append(self.level_)  # 诉讼等级8
        tmp.append("1" if self.is_foreign_ else "0")  # 是否涉外9
        tmp.append("#".join(self.to_db(self.yuangao_)))  # 原告10-16
        tmp.append("#".join(self.to_db(self.beigao_)))  # 被告17-23
        tmp.append("#".join(self.to_db(self.third_people_)))  # 第三人24-30

        faguans = [p.name_ for p in self.presiding_judge_]  # 审判长31
        shenpanyuan = [p.name_ for p in self.judges_]  # 审判员32
        peishenyuan = [p.name_ for p in self.juror_]  # 陪审员33
        shujiyuan = [p.name_ for p in self.clerk_]  # 书记员34
        faguanzhuli = [p.name_ for p in self.judge_assistant_]  # 法官助理35
        tmp.append(",".join(faguans))
        tmp.append(",".join(shenpanyuan))
        tmp.append(",".join(peishenyuan))
        tmp.append(",".join(shujiyuan))
        tmp.append(",".join(faguanzhuli))
        # tmp.append(self.trademark_id_)											#商标号36
        # tmp.append(self.patent_id_)												#专利号37
        judge_result = "" if len(self.judge_results_) == 0\
            else self.judge_results_[
            len(self.judge_results_) - 1]
        tmp.append(judge_result)  # 判决结果38
        yishenanhao = ""
        ershenanhao = ""
        sanshenanhao = ""
        yishenjieguo = ""
        ershenjieguo = ""
        sanshenjieguo = ""
        if self.level_ == "二审":
            ershenanhao = self.number_
            ershenjieguo = judge_result
            yishenjieguo = "" if len(self.judge_results_) < 2 else "~".join(
                self.judge_results_[:-1])
            yishenanhao = "" if len(
                self.pre_judge_) == 0 else self.pre_judge_[0]
        elif self.level_ == "一审":
            yishenanhao = self.number_
            yishenjieguo = judge_result
        elif self.level_ == "三审":
            sanshenanhao = self.number_
            yishenanhao = "" if len(
                self.pre_judge_) != 2 else self.pre_judge_[0]
            ershenanhao = "" if len(self.pre_judge_) == 0 else self.pre_judge_[
                len(self.pre_judge_) - 1]
            sanshenjieguo = judge_result
            ershenjieguo = "" if len(
                self.judge_results_) < 2 else self.judge_results_[-2]
            yishenjieguo = "" if len(self.judge_results_) < 3 else "~".join(
                self.judge_results_[:-1])
        tmp.append(yishenanhao)  # 一审案号39
        tmp.append(ershenanhao)  # 二审审案号40
        tmp.append(self.judge_time_)
        tmp.append(sanshenanhao)  # 三审审案号40
        tmp.append(yishenjieguo)  # 一审结果
        tmp.append(ershenjieguo)  # 二审结果
        tmp.append(sanshenjieguo)  # 三审结果
        caijueshuhao = ""
        if self.trademark_id_ != "":
            caijueshuhao = self.trademark_id_
        elif self.patent_id_ != "":
            caijueshuhao = self.patent_id_
        tmp.append(caijueshuhao)
        return "#".join(tmp)

    def to_db(self, parties):
        """."""
        names = []
        address = []
        countries = []
        proxies_name = []
        proxies_company = []
        proxies_title = []
        legal_representatives = []
        for party in parties:
            names.append(party.person_.name_)
            address.append(party.person_.address_)
            countries.append(party.person_.country_)
            for p in party.legal_representative_:
                legal_representatives.append(p.name_)
            if len(party.legal_representative_) == 0:
                legal_representatives.append("")
            if len(party.proxy_) == 0:
                p = Person()
                party.proxy_.append(p)
            for p in party.proxy_:
                proxies_name.append(p.name_)
                proxies_company.append(p.company_)
                proxies_title.append(p.title_)
        return [
            self.to_combination_str(names), self.to_combination_str(address),
            self.to_combination_str(countries),
            self.to_combination_str(legal_representatives),
            self.to_combination_str(proxies_name),
            self.to_combination_str(proxies_company),
            self.to_combination_str(proxies_title)]

    def to_combination_str(self, data_list):
        """."""
        return ",".join(data_list)

    def to_json(self):
        """."""
        yuangao = [p.to_csv() for p in self.yuangao_]
        beigao = [p.to_csv() for p in self.beigao_]
        third_people = [p.to_csv() for p in self.third_people_]
        tmp = "审理法院 : %s\n" % self.court_
        tmp += "法院级别 : %s\n" % self.court_level_
        tmp += "是否涉外 : %s\n" % ("是" if self.is_foreign_ else "否")
        tmp += "案件号 : %s\n" % self.number_
        tmp += "立案年度 : %s\n" % self.year_to_accept_
        tmp += "案件地区 : %s\n" % self.area_
        tmp += "案件性质 : %s\n" % self.nature_
        tmp += "文书类型 : %s\n" % self.type_
        tmp += "案件开始时间 : %s\n" % self.start_time_
        tmp += "诉讼等级 : %s\n" % self.level_
        tmp += "上一级诉讼号 : %s\n" % (",".join(self.pre_judge_))
        tmp += "判决时间 : %s\n" % self.judge_time_
        tmp += "裁决结果 : %s\n" % self.judge_result_
        tmp += "原告 : %s\n" % "~".join(yuangao)
        tmp += "被告 : %s\n" % "~".join(beigao)
        tmp += "第三人 : %s\n" % "~".join(third_people)
        tmp += "审判长 : %s\n" % "~".join([judge.to_csv()
                                        for judge in self.presiding_judge_])
        tmp += "审判员 : %s\n" % "~".join([judge.to_csv()
                                        for judge in self.judges_])
        tmp += "陪审员 : %s\n" % "~".join([judge.to_csv()
                                        for judge in self.juror_])
        tmp += "书记员 : %s\n" % "~".join([judge.to_csv()
                                        for judge in self.clerk_])
        tmp += "法官助理 : %s\n" % self.judge_assistant_.to_csv()
        tmp += "审理时间 : %s\n" % self.judge_time_
        return tmp
