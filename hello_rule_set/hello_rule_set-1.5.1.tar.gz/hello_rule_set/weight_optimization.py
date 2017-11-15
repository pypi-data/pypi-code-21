# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import random
import time
import math


class geneticoptimize(object):
    """docstring for geneticoptimize
    --------------------------------------------------------------------------------
    Parameter Description
    rule_list：规则，取值
    x：用于训练的特征
    y：用于训练的标签
    popsize：种群大小
    mutprob：变异概率
    maxmut_prop：变异的染色体长度最大比例
    elite：生存比例
    maxiter：繁衍代数
    beta:beta越大召回率影响越大,beta=1时同样重要，beta取大于0的实数
    risk_score:判为拒绝的分数
    由于演化时间较长，演化的时候会有最优值输出，如果对当前结果已经满意，或者算法已经陷入局部最优，
    那么可以提前终止程序，然后可以用classname.scores来获得当前种群所有生物适应分和染色体
    --------------------------------------------------------------------------------
    For example:
        if __name__=="__main__":
            import pandas as pd
            from sklearn.cross_validation import train_test_split
            import hello_rule_set.weight_optimization as wo

            data = pd.read_csv("buding_label1.csv")
            data = data.fillna(0)
            del data["sequence_label"]
            data.iloc[:, 1:] = data.iloc[:, 1:].astype("float")
            x_all = data.iloc[:, 1:]
            y_all = data['label']

            x_train, x_other, y_train, y_other = train_test_split(
                x_all, y_all, test_size=0.5)
            x_validation, x_test, y_validation, y_test = train_test_split(
                x_other, y_other, test_size=6.0 / 8)

            rule_list = {
            "3个月内申请信息关联多个身份证": [[0, 10, 1, [1,10,"+"]], [0, 5, 0.5, 30]],
            "3个月内申请人手机号作为联系人手机号出现的次数大于等于2":[[5, 20, 1, [1,10,"+"]], [0, 0, 0, 30]],
            "7天内设备或身份证或手机号申请次数过多": [[0, 10, 1, [1,10,"-"]], [0, 0, 0, 30]],
            "1个月内设备或身份证或手机号申请次数过多": [[0, 10, 1, [0,10,"+"]], [0, 0, 0, 30]],
            "1天内身份证使用过多设备进行申请": [[5, 30, 1, [3,10,"-"]], [0, 0, 0, 30]],
            "7天内身份证使用过多设备进行申请": [[10, 35, 1, [1,10,"+"]], [0, 0, 0, 30]],
            "1个月内身份证使用过多设备进行申请": [[10, 35, 1, [1,10,"+"]], [0, 0, 0, 30]],
            "7天内申请人在多个平台申请借款": [[0, 5, 1, [1,10,"+"]], [0, 10, 0.5, 30]],
            "1个月内申请人在多个平台申请借款": [[0, 5, 1, [1,10,"+"]], [0, 6, 0.5, 30]],
            "3个月内申请人在多个平台申请借款": [[0, 5, 1, [1,10,"+"]], [0, 5, 0.5, 30]],
            "3个月内借款人身份证关联多个申请信息": [[0, 10, 1, [1,10,"+"]], [0, 0, 0, 30]]}

            BETA = 0.5
            test = wo.geneticoptimize(rule_list, x_train, y_train, popsize=100,
                                      mutprob=0.3, maxmut_prop=0.5, elite=0.1, maxiter=100, beta=BETA)
            score = test.evolution()

            score = test.scores
            gene = score[0][1]

            test_score=test.predict(x_test,gene)
            rule_weight=test.rule_weight(gene)
            # 保存
            with open("test.pkl", "w") as file:
                pickle.dump(test,file)
            # 读取
            with open("test.pkl", "r") as file:
                new_model = pickle.load(file)

    """

    def __init__(self, rule_list, x, y, popsize=100, mutprob=0.3, maxmut_prop=0.2,
                 elite=0.3, maxiter=20, beta=1, risk_score=80, missing="-999", positive=1):
        super(geneticoptimize, self).__init__()
        self.rule_list = rule_list
        self.popsize = popsize
        self.mutprob = mutprob
        self.maxmut_prop = maxmut_prop
        self.elite = elite
        self.maxiter = maxiter
        self.beta = beta
        self.x = x
        self.y = y
        self.scores = []
        self.risk_score = risk_score
        self.positive = positive
        self.missing = missing

    # def get_rule_list(self, path):
    #     weight_df = pd.read_excel(path).fillna("0.0")
    #     weight_df.drop(weight_df.columns[0], axis=1, inplace=True)
    #     weight_df.drop(0, axis=0, inplace=True)
    #     weight_df.columns = ["rule", "weight"]
    #     weight_df["weight"] = [_.split("*")[0]
    #                            for _ in weight_df["weight"].tolist()]
    #
    #     def _split_(_):
    #         splited = _.split("+")
    #         try:
    #             return splited[1]
    #         except IndexError:
    #             return 0
    #     weight_df["w1"] = [_.split("+")[0]
    #                        for _ in weight_df["weight"].tolist()]
    #     weight_df["w2"] = [_split_(_) for _ in weight_df["weight"].tolist()]
    #     weight_df.drop("weight", axis=1, inplace=True)
    #     weight_df[["w1", "w2"]] = weight_df[["w1", "w2"]].astype("float")

    def row_score(self, input, vec, rang):
        """method's help string.
        ----------------------
        Parameter Description
        vec:自然数染色体
        rang:取值范围
        ----------------------
        return :染色体得分
        ----------------------
        """
        w1 = []
        w2 = []

        [w1.append(round(vec[c])) for c in range(len(vec)) if c % 2 == 0]
        [w2.append(round(vec[c], 2)) for c in range(len(vec)) if c % 2 != 0]

        row_score = pd.DataFrame()
        columns = self.x.columns.tolist()

        def cal_col(c):
            i = columns.index(c)
            val_area = rang[i * 2][3]
            if val_area[-1] == "+":  # 正向指标
                output = [w1[i] + round(min((q - val_area[0]) * w2[i], rang[(i + 1) * 2 - 1][3]))
                          if q >= val_area[0] and q <= val_area[1] and q != self.missing else 0 for q in input[c].tolist()]
                # output = map(lambda q: w1[i] + round(min(（rang[i * 2][3]) - q） * w2[i], rang[(i + 1) * 2 - 1][3])) if q >= rang[i * 2][3] and q != self.missing else 0, self.x[c])
            elif val_area[-1] == "-":  # 负向指标
                output = [w1[i] + round(min((val_area[1] - q) * w2[i], rang[(i + 1) * 2 - 1][3]))
                          if q >= val_area[0] and q <= val_area[1] and q != self.missing else 0 for q in input[c].tolist()]
                # output = map(lambda q: w1[i] + round(min((abs(rang[i * 2][3]) - q) * w2[i], rang[(i + 1) * 2 - 1][3])) if q <= abs(rang[i * 2][3]) and q != self.missing else 0, self.x[c])
            else:
                raise("feature direction only '+' or '-'")
            row_score[c] = output

        [cal_col(c) for c in columns]
        # row_score[columns] = pd.DataFrame([cal_col(c) for c in columns]).T
        # row_score[columns]= map(lambda x: cal_col(x), columns)
        row_score["col_sum"] = np.array(row_score).sum(axis=1)
        return row_score

    # 适应度函数
    def costf(self, vec, rang):
        """method's help string.
        ----------------------
        Parameter Description
        vec:自然数染色体
        rang:取值范围
        ----------------------
        return :染色体得分
        ----------------------
        """
        # w1 = []
        # w2 = []

        # [w1.append(vec[c]) for c in range(len(vec)) if c % 2 == 0]
        # [w2.append(vec[c]) for c in range(len(vec)) if c % 2 != 0]

        # row_score = pd.DataFrame()
        # columns = []
        # [columns.append(c) for c in self.x.columns]

        # for c in columns:
        #     i = columns.index(c)
        #     if rang[(i + 1) * 2 - 1][3] > 0:
        #         row_score[c] = map(lambda q: w1[i] + min(q * w2[i], rang[(i + 1) * 2 - 1][3]) if q >= rang[i * 2][3] else 0, self.x[c])
        #     else:
        #         row_score[c] = map(lambda q: w1[i] + max(q * w2[i], rang[(i + 1) * 2 - 1][3]) if q >= rang[i * 2][3] else 0, self.x[c])

        # row_score["col_sum"] = row_score.apply(lambda c: c.sum(), axis=1)
        row_score = self.row_score(self.x, vec, rang)
        result = pd.DataFrame()
        result["score"] = row_score["col_sum"]
        label = pd.DataFrame(self.y)
        label = label.reset_index()
        del label["index"]
        result = pd.concat([result, label], axis=1)
        result["predict"] = [
            1 if c >= self.risk_score else 0 for c in result["score"].tolist()]

        # result["predict"]=map(
        #     lambda c: 1 if c >= self.risk_score else 0, result["score"])

        try:
            col_rep = self.y.name
        except AttributeError:
            col_rep = self.y.columns[0]
        result.rename(index=str, columns={col_rep: "label"}, inplace=True)

        # 混淆矩阵
        confusion_matrix = np.array([[len(result[(result['predict'] == 0) & (result['label'] == 0)]), len(result[(result['predict'] == 1) & (result['label'] == 0)])],
                                     [len(result[(result['predict'] == 0) & (result['label'] == 1)]), len(result[(result['predict'] == 1) & (result['label'] == 1)])]])

        # 评价指标
        if self.positive == 1:
            try:
                P1 = float(confusion_matrix[1, 1]) / \
                    confusion_matrix[:, 1].sum()
                R1 = float(confusion_matrix[1, 1]) / \
                    confusion_matrix[1, :].sum()
                F1 = (1 + self.beta**2) / (1 / P1 + self.beta**2 / R1)

            except ZeroDivisionError:
                P1, R1, F1 = 0, 0, 0

            if R1 == 1:
                return 0
            else:
                return F1
        elif self.positive == 0:
            try:
                P1 = float(confusion_matrix[0, 0]) / \
                    confusion_matrix[:, 0].sum()
                R1 = float(confusion_matrix[0, 0]) / \
                    confusion_matrix[0, :].sum()
                F1 = (1 + self.beta**2) / (1 / P1 + self.beta**2 / R1)
            except ZeroDivisionError:
                P1 = 0
                R1 = 0
                F1 = 0

            if R1 == 1:
                return 0
            else:
                return F1
        else:
            raise Exception(u"positive只可以取值0或1")

    def PRF_cal(self, vec, rang, mode="all"):
        """method's help string.
        ----------------------
        Parameter Description
        vec:自然数染色体
        rang:取值范围
        mode:需要计算说明,可以取"all","recall","accuracy"
        ----------------------
        return:Recall,Accuracy or F_beta
        ----------------------
        """
        row_score = self.row_score(self.x, vec, rang)
        result = pd.DataFrame()
        result["score"] = row_score["col_sum"]
        label = pd.DataFrame(self.y)
        label = label.reset_index()
        del label["index"]
        result = pd.concat([result, label], axis=1)
        result["predict"] = [
            1 if _ >= self.risk_score else 0 for _ in result["score"].tolist()]

        # result["predict"]= map(
        #     lambda _: 1 if _ >= self.risk_score else 0, result["score"])

        try:
            col_rep = self.y.name
        except AttributeError:
            col_rep = self.y.columns[0]
        result.rename(index=str, columns={col_rep: "label"}, inplace=True)

        # 混淆矩阵
        confusion_matrix = np.array([[len(result[(result['predict'] == 0) & (result['label'] == 0)]), len(result[(result['predict'] == 1) & (result['label'] == 0)])],
                                     [len(result[(result['predict'] == 0) & (result['label'] == 1)]), len(result[(result['predict'] == 1) & (result['label'] == 1)])]])

        # 评价指标
        if self.positive == 1:
            try:
                P1 = float(confusion_matrix[1, 1]) / \
                    confusion_matrix[:, 1].sum()
                R1 = float(confusion_matrix[1, 1]) / \
                    confusion_matrix[1, :].sum()

            except ZeroDivisionError:
                P1 = 0
                R1 = 0
        elif self.positive == 0:
            try:
                P1 = float(confusion_matrix[0, 0]) / \
                    confusion_matrix[:, 0].sum()
                R1 = float(confusion_matrix[0, 0]) / \
                    confusion_matrix[0, :].sum()
            except ZeroDivisionError:
                P1 = 0
                R1 = 0

        else:
            raise Exception(u"positive只可以取值0或1")

        try:
            F1 = (1 + self.beta**2) / (1 / P1 + self.beta**2 / R1)
        except ZeroDivisionError:
            F1 = 0

        if mode == "all":
            return F1
        elif mode == "recall":
            return R1
        elif mode == "accuracy":
            return P1
        else:
            raise Exception(u"mode参数没有%s类型" % (mode))

    # 获取参数取值范围
    def get_rang(self, rule_list):
        """method's help string.
        ------------------------------------------------------
        Parameter Description
        rule_list:规则限制列表,即类中的__init__变量
        ------------------------------------------------------
        return:参数取值范围,格式如[w(1)1,w(1)2,...,w(n)1,w(n)2]
        ------------------------------------------------------
        """
        output = []
        column = self.x.columns.tolist()
        for c in column:
            try:
                output.append(rule_list[c.encode("utf8")][0])
                output.append(rule_list[c.encode("utf8")][1])
            except ValueError:
                output.append(rule_list[c][0])
                output.append(rule_list[c][1])
        return output

    # 根据参数的取值范围和精度要求获得单个染色体长度
    def get_bitlength(self, rang):
        """method's help string.
        --------------------------
        Parameter Description
        rang:参数取值范围
        --------------------------
        return:单个染色体长度
        --------------------------
        """
        if rang[1] > rang[0]:
            N = np.ceil((rang[1] - rang[0]) / rang[2]) + 1
            bitlength = np.int(np.ceil(np.log2(N)))
            return bitlength
        else:
            return 1

    # 获取染色体长度列表
    def get_bitlength_list(self, rang):
        output = []
        for _ in rang:
            output.append(self.get_bitlength(_))
        return output

    # 解码
    def to2_10(self, binlist):
        val = 0
        pow = 1
        for i in range(len(binlist))[:: -1]:
            val += binlist[i] * pow
            pow *= 2
        return float(val)

    # 2进制编码转换成10进制批处理
    def trans2to10(self, pop2, leninfo, rang):
        row, column = pop2.shape
        pop10 = np.zeros((row, len(leninfo)))
        for i in range(row):
            star = 0
            for j in range(len(leninfo)):
                end = star + leninfo[j]
                try:
                    pop10[i][j] = self.to2_10(
                        pop2[i][star:end]) / pow(2, leninfo[j]) * (rang[j][1] - rang[j][0]) + rang[j][0]
                except ZeroDivisionError:
                    pop10[i][j] = rang[j][1]
                star = end
        return pop10

    # 获取初始种群
    def getpop2(self, leninfo):
        pop2 = np.random.rand(self.popsize, sum(leninfo))
        pop2[pop2 > 0.5] = 1
        pop2[pop2 <= 0.5] = 0
        return pop2

    # 取反变异
    # def self.mutate(vec,maxmut_prop):
    #   length=int(len(vec)*maxmut_prop)
    #   star=random.randint(1,len(vec)-length)
    #   end=star+length
    #   gene=vec[star:end]
    #   for i in range(len(gene)):
    #       gene[i]=1-gene[i]
    #   output=np.zeros(len(vec))
    #   output[:star]=vec[:star]
    #   output[star:end]=gene
    #   output[end:]=vec[end:]
    #   return output

    # 异或变异
    def mutate(self, vec1, vec2):
        length = int(len(vec1) * self.maxmut_prop)
        star = random.randint(1, len(vec1) - length)
        end = star + length
        gene1 = vec1[star:end]
        gene2 = vec2[star:end]
        for i in range(len(gene1)):
            if (gene1[i] and (not gene2[i])) or ((not gene1[i]) and gene2[i]):
                gene1[i] = 1
            else:
                gene1[i] = 0
        output = np.zeros(len(vec1))
        output[:star] = vec1[:star]
        output[star:end] = gene1
        output[end:] = vec1[end:]
        return output

    # 交叉
    def crossover(self, r1, r2):
        i = random.randint(1, len(r1) - 2)
        output = np.zeros(len(r1))
        output[:i] = r1[:i]
        output[i:] = r2[i:]
        return output

    # 轮盘赌
    def select_sample_index(self, scores):
        fit = []
        [fit.append(score[0]) for score in scores]
        fit_add = []
        [fit_add.append(f + random.random()) for f in fit]
        return fit_add.index(max(fit_add))

    def array2str(self, arr):
        output = ""
        for i in range(len(arr)):
            output += str(int(arr[i]))
        return output

    def str2array(self, string):
        output = np.zeros(len(string))
        for i in range(len(string)):
            output[i] = float(string[i])
        return output

    def issame(self, new_sample, pop2):
        max_sum = 0
        for i in range(pop2.shape[0]):
            tmp = (pop2[i] == new_sample).sum()
            if tmp > max_sum:
                max_sum = tmp
        return max_sum

    def predict(self, x, gene):
        """method's help string.
        -------------------------------
        Parameter Description
        x:要预测的数据
        gene:用于预测的染色体
        -------------------------------
        return:每个样本的每条规则得分和总分
        -------------------------------
        """
        rang = self.get_rang(self.rule_list)
        leninfo = self.get_bitlength_list(rang)
        x = x
        gene2 = self.str2array(gene)
        try:
            gene10 = self.trans2to10(gene2, leninfo, rang)[0]
        except ValueError:
            gene10 = self.trans2to10(gene2.reshape(
                1, len(gene2)), leninfo, rang)[0]
        return self.row_score(x, gene10, rang)

    def rule_weight(self, gene):
        """method's help string.
        -------------------------------
        Parameter Description
        gene:用于预测的染色体
        -------------------------------
        return:每条规则的规则名，权重，触发阈值和方向
        -------------------------------
        """
        # 返回规则名，权重，触发阈值和方向
        rang = self.get_rang(self.rule_list)
        leninfo = self.get_bitlength_list(rang)
        gene2 = self.str2array(gene)
        try:
            gene10 = self.trans2to10(gene2, leninfo, rang)
        except ValueError:
            gene10 = self.trans2to10(
                gene2.reshape(1, len(gene2)), leninfo, rang)

        w1 = []
        w2 = []
        [w1.append(round(gene10[0][i]))
         for i in range(len(gene10[0])) if i % 2 == 0]
        [w2.append(round(gene10[0][i], 2))
         for i in range(len(gene10[0])) if i % 2 != 0]
        rule_output = []
        for i in range(len(w1)):
            rule_output.append(
                [self.x.columns[i], (w1[i], w2[i]), rang[i * 2][-1]])
        return pd.DataFrame(rule_output, columns=["rule", "weight", "value"])

    # 迭代函数
    def evolution(self, time_show=False):
        """method's help string.
        -------------------------------
        Parameter Description
        time_show:为True时可以显示每一代结束当前时间
        -------------------------------
        return:最后一代种群中每个个体的基因和适应度值
        -------------------------------
        """
        # 获取参数取值范围,染色体长度
        rang = self.get_rang(self.rule_list)
        leninfo = self.get_bitlength_list(rang)

        # 获取初始种群
        pop2 = self.getpop2(leninfo)

        # 每一代有多少胜出者
        topelite = int(self.elite * self.popsize)

        # 演化
        for i in range(self.maxiter):
            # 物竞
            pop10 = self.trans2to10(pop2, leninfo, rang)
            scores = []
            [scores.append([self.costf(pop10[j], rang), self.array2str(pop2[j])])
             for j in range(self.popsize)]
            scores.sort()
            scores.reverse()

            # 天择
            pop_win = scores[0:topelite]
            pop2_next = np.zeros((len(pop_win), sum(leninfo)))
            for j in range(topelite):
                pop2_next[j] = self.str2array(pop_win[j][1])

            # 适者生存
            while len(pop2_next) < self.popsize:
                if random.random < self.mutprob:
                    # 取反变异
                    # c=random.randint(0,topelite-1)
                    # new_sample=self.mutate(self.str2array(pop_win[c][1]))
                    # pop2=np.concatenate((pop2,new_sample.reshape(1,len(new_sample))))

                    # 异或变异
                    new_sample = pop2_next[0]
                    while self.issame(new_sample, pop2_next) == pop2_next.shape[1]:
                        c1 = self.select_sample_index(scores)
                        c2 = self.select_sample_index(scores)
                        new_sample = self.mutate(self.str2array(
                            pop2[c1], self.str2array(pop2[c2])))
                    pop2 = np.concatenate(
                        (pop2_next, new_sample.reshape(1, len(new_sample))))
                else:
                    # 交叉
                    new_sample = pop2_next[0]
                    while self.issame(new_sample, pop2_next) == pop2_next.shape[1]:
                        c1 = self.select_sample_index(scores)
                        c2 = self.select_sample_index(scores)
                        r1 = self.str2array(pop2[c1])
                        r2 = self.str2array(pop2[c2])
                        new_sample = self.crossover(r1, r2)
                    pop2_next = np.concatenate(
                        (pop2_next, new_sample.reshape(1, len(new_sample))))

            best = self.str2array(scores[0][1])
            print u"当前代数:", i, u"当前种群中最优值:", scores[0][0], u"最优值准确率:", self.PRF_cal(self.trans2to10(best.reshape(1, len(best)), leninfo, rang)[0], rang, "accuracy"), u"最优值召回率:", self.PRF_cal(self.trans2to10(best.reshape(1, len(best)), leninfo, rang)[0], rang, "recall")
            # ,u"当前种群中最优解:",self.trans2to10(best.reshape(1,len(best)),leninfo,rang)

            pop2 = pop2_next
            now = int(time.time())
            timeArray = time.localtime(now)
            otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            if time_show:
                print otherStyleTime
            try:
                self.scores[0][0]
                if scores[0][0] > self.scores[0][0]:
                    self.scores = scores
            except IndexError:
                self.scores = scores

        return scores


def percentile(data, label="label", exclude_column=["label"], per=10):
    """method's help string.
    ---------------------------------------------------------------------------------------
    percentile函数用于计算黑白样本的指标分布情况，即分位数
    Parameter Description
        data:传入的pandas dataframe
        label:标签列的列名,defult:"label"
        exclude_column:需要排出的列,defult:["label"]
        per:分位数步长,defult:10
    ---------------------------------------------------------------------------------------
    Return
        per_all,per_white,per_black分别为所有样本,白样本,黑样本分布情况
    ---------------------------------------------------------------------------------------
    For Example
        import weight_optimization as wo
        per_all,per_white,per_black=wo.percentile(data,exclude_column=["label","uuid"])
    ---------------------------------------------------------------------------------------
    """
    column = [c for c in data.columns.tolist() if c not in exclude_column]

    data_white = data[data["label"] == 0]
    data_black = data[data["label"] == 1]

    per_all, per_white, per_black = [pd.DataFrame(columns=column)] * 3

    def per_col(c):
        per_all[c] = [np.percentile(data[c], i) for i in range(0, 100, per)]
        per_white[c] = [np.percentile(data_white[c], i)
                        for i in range(0, 100, per)]
        per_black[c] = [np.percentile(data_black[c], i)
                        for i in range(0, 100, per)]
    [per_col(c) for c in column]
    per_all.index, per_white.index, per_black.index = [range(0, 100, per)] * 3
    return per_all, per_white, per_black

# 计算测试集和获取规则权重


def get_weight_and_index(string, rang, rule_list, x, y, beta, risk_score=80):

    def get_rang(rule_list):
        output = []
        for rang_cuple in rule_list:
            output.append(rang_cuple[1][0])
            output.append(rang_cuple[1][1])
        return output

    def get_bitlength(rang):
        if rang[1] > rang[0]:
            N = np.ceil((rang[1] - rang[0]) / rang[2]) + 1
            bitlength = np.int(np.ceil(np.log2(N)))
            return bitlength
        else:
            return 1

    def get_bitlength_list(rang):
        output = []
        for _ in rang:
            output.append(get_bitlength(_))
        return output

    def str2array(string):
        output = np.zeros(len(string))
        for i in range(len(string)):
            output[i] = float(string[i])
        return output

    def to2_10(binlist):
        val = 0
        pow = 1
        for i in range(len(binlist))[::-1]:
            val += binlist[i] * pow
            pow *= 2
        return float(val)

    def trans2to10(pop2, leninfo, rang):
        row, column = pop2.shape
        pop10 = np.zeros((row, len(leninfo)))
        for i in range(row):
            star = 0
            for j in range(len(leninfo)):
                end = star + leninfo[j]
                try:
                    pop10[i][j] = to2_10(
                        pop2[i][star:end]) / pow(2, leninfo[j]) * (rang[j][1] - rang[j][0]) + rang[j][0]
                except ZeroDivisionError:
                    pop10[i][j] = rang[j][1]
                star = end
        return pop10

    def PRF_cal(vec, x=x, y=y, rang=rang, beta=beta, mode="all", risk_score=risk_score, positive=1):
        w1 = []
        w2 = []

        [w1.append(round(vec[c])) for c in range(len(vec)) if c % 2 == 0]
        [w2.append(round(vec[c], 1)) for c in range(len(vec)) if c % 2 != 0]

        row_score = pd.DataFrame()
        columns = []
        [columns.append(c) for c in x.columns]
        for c in columns:
            i = columns.index(c)
            if rang[i * 2][3] > 0:
                row_score[c] = map(lambda q: w1[i] + round(
                    min(q * w2[i], rang[(i + 1) * 2 - 1][3])) if q >= rang[i * 2][3] else 0, x[c])
            else:
                row_score[c] = map(lambda q: w1[i] + round(min((abs(rang[i * 2][3]) - q) * w2[i],
                                                               rang[(i + 1) * 2 - 1][3])) if q <= abs(rang[i * 2][3]) else 0, x[c])
        row_score["col_sum"] = row_score.apply(lambda c: c.sum(), axis=1)
        result = pd.DataFrame()
        result["score"] = row_score["col_sum"]
        label = pd.DataFrame(y)
        label = label.reset_index()
        del label["index"]
        result = pd.concat([result, label], axis=1)
        result["predict"] = map(
            lambda _: 1 if _ >= risk_score else 0, result["score"])

        try:
            col_rep = y.name
        except AttributeError:
            col_rep = y.columns[0]
        result.rename(index=str, columns={col_rep: "label"}, inplace=True)

        # 混淆矩阵
        confusion_matrix = np.array([[len(result[(result['predict'] == 0) & (result['label'] == 0)]), len(result[(result['predict'] == 1) & (result['label'] == 0)])],
                                     [len(result[(result['predict'] == 0) & (result['label'] == 1)]), len(result[(result['predict'] == 1) & (result['label'] == 1)])]])

        if positive == 1:
            try:
                P1 = float(confusion_matrix[1, 1]) / \
                    confusion_matrix[:, 1].sum()
                R1 = float(confusion_matrix[1, 1]) / \
                    confusion_matrix[1, :].sum()
            except ZeroDivisionError:
                P1 = 0
                R1 = 0
        elif positive == 0:
            try:
                P1 = float(confusion_matrix[0, 0]) / \
                    confusion_matrix[:, 0].sum()
                R1 = float(confusion_matrix[0, 0]) / \
                    confusion_matrix[0, :].sum()
            except ZeroDivisionError:
                P1 = 0
                R1 = 0
        else:
            raise Exception(u"positive只可以取值0或1")

        try:
            F1 = (1 + beta**2) / (1 / P1 + beta**2 / R1)
        except ZeroDivisionError:
            F1 = 0

        if mode == "all":
            return F1
        elif mode == "recall":
            return R1
        elif mode == "accuracy":
            return P1
        else:
            raise Exception(u"mode参数没有%s类型" % (mode))

    rang = get_rang(rule_list)
    leninfo = get_bitlength_list(rang)
    gene2 = str2array(string)
    try:
        gene10 = trans2to10(gene2, leninfo, rang)
    except ValueError:
        gene10 = trans2to10(gene2.reshape(1, len(gene2)), leninfo, rang)

    w1 = []
    w2 = []
    [w1.append(math.ceil(gene10[0][_]))
     for _ in range(len(gene10[0])) if _ % 2 == 0]
    [w2.append(math.ceil(gene10[0][_]))
     for _ in range(len(gene10[0])) if _ % 2 != 0]

    rule_output = []
    for _ in range(len(w1)):
        rule_output.append([rule_list[_][0], (w1[_], w2[_])])

    P = PRF_cal(gene10[0], x=x, y=y, rang=rang, beta=beta, mode="accuracy")
    R = PRF_cal(gene10[0], x=x, y=y, rang=rang, beta=beta, mode="recall")
    F = PRF_cal(gene10[0], x=x, y=y, rang=rang, beta=beta, mode="all")
    return rule_output, P, R, F
