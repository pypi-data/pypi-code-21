# _*_ coding:utf-8 _*_
import pandas as pd
import time
import itertools
try:
    sparkSession = sqlContext
    from pyspark.sql.functions import udf
    from pyspark.sql.types import IntegerType
except NameError:
    pass

# 字符串格式时间转换为时间戳


def timestr2stamp(timestr, time_format="%Y-%m-%d %H:%M:%S"):
    timeArray = time.strptime(str(timestr), time_format)
    timeStamp = int(time.mktime(timeArray))
    return timeStamp

# 时间戳转换为字符串格式时间


def stamp2timestr(timeStamp, time_format="%Y-%m-%d %H:%M:%S"):
    return time.strftime(time_format, time.localtime(timeStamp))


def get_time_day(year, month, day):
    if len(str(month)) == 1:
        month = "0" + str(month)
    if len(str(day)) == 1:
        day = "0" + str(day)
    return str(year) + str(month) + str(day)


# 单条规则的命中率，准确率
def rule_hit_acc_from_rulelist(data, label="label", is_pandas=True, is_cache=True):
    """method's help string
    data:传入的dataframe,只支持spark的dataframe
    label:默认"label",标签列名
    is_pandas:默认True,在运算过程中是否转成pandas dataframe，单机运算，若数据量较大则选择False
    is_cache:默认True,在运算过程中是否cache,加速运算，只在is_pandas=False时生效，若若数据量极大则选择False
    """

    try:
        grouped = data.groupBy("ruleList").count()
    except KeyError:
        grouped = data.groupBy("rulelist").count()
    grouped = grouped.toPandas()
    ruleList = grouped.columns[0]
    rule_count = []
    for i in range(len(grouped)):
        count = grouped.at[i, "count"]
        try:
            for rule in grouped.at[i, ruleList]:
                rule_count.append([rule, count])
        except TypeError:
            pass

    # 规则命中
    rule_count = pd.DataFrame(rule_count, columns=["rule", "hit"]).groupby(
        "rule", as_index=False).count()

    def rule_in(rule, rulelist):  # 规则准确率
        if rulelist:
            if rule in rulelist:
                return 1
        else:
            return 0

    for i in range(len(rule_count)):
        rule = rule_count.at[i, "rule"]
        hit_udf = udf(lambda x: rule_in(rule, x), IntegerType())
        data = data.withColumn(rule, hit_udf(data[ruleList]))

    if is_pandas:
        df = data.toPandas()
        try:
            rule_acc = pd.DataFrame([[rule, len(df[(df["label"] == 1) & (df[rule] == 1)])
                                      / float(len(df[(df[rule] == 1)]))] for rule in rule_count["rule"]], columns=["rule", "acc"])
        except KeyError:
            rule_acc = pd.DataFrame([[rule, len(df[(df["label"] == 1) & (df[rule.encode("utf8")] == 1)])
                                      / float(len(df[(df[rule.encode("utf8")] == 1)]))] for rule in rule_count["rule"]], columns=["rule", "acc"])

    else:
        # 是否cache
        if is_cache:
            data.cache().count()
        try:
            rule_acc = pd.DataFrame([[rule, data.filter((data["label"] == 1) & (data[rule] == 1)).count()
                                      / float(data.filter(data[rule] == 1).count())] for rule in rule_count["rule"]], columns=["rule", "acc"])
        except KeyError:
            rule_acc = pd.DataFrame([[rule, data.filter((data["label"] == 1) & (data[rule.encode("utf8")] == 1)).count()
                                      / float(data.filter(data[rule.encode("utf8")] == 1).count())] for rule in rule_count["rule"]], columns=["rule", "acc"])

    output_all = pd.merge(rule_count, rule_acc, on="rule").sort(
        "hit", ascending=False)

    # 分天的命中率
    get_time_day_udf = udf(
        lambda year, month, day: get_time_day(year, month, day))
    data = data.withColumn("time_day", get_time_day_udf(
        data["year"], data["month"], data["day"]))
    grouped_day = data.groupBy("time_day", ruleList).count().toPandas()
    rule_count_day = []
    time_day = grouped_day["time_day"].drop_duplicates().tolist()
    for t in time_day:
        day_t = grouped_day[grouped_day["time_day"] == t]
        for i in day_t.index:
            count = day_t.at[i, "count"]
            try:
                for rule in day_t.at[i, ruleList]:
                    rule_count_day.append([t, rule, count])
            except TypeError:
                pass

    # 规则命中
    rule_count_day = pd.DataFrame(rule_count_day, columns=["time_day", "rule", "hit"]).groupby(["time_day",
                                                                                                "rule"], as_index=False).count()
    return output_all, rule_count_day


def rule_hit_acc_from_poc(data, column, label="label", timestr="time", time_format="%Y-%m-%d %H:%M:%S"):
    """method's help string
    data:传入的dataframe,只支持pandas的dataframe
    column:需要计算的列名，list格式或单个的字符串格式
    label:默认"label",标签列名
    """
    data_count = len(data)

    def column_hit_acc(c):
        count_hit = float(len(data[data[c] > 0]))
        hit = count_hit / data_count
        try:
            acc = len(data[(data[c] > 0) & (data[label] == 1)]) / count_hit
        except ZeroDivisionError:
            acc = 0
        return [c, hit, acc]

    output = pd.DataFrame(data[column].apply(lambda x: column_hit_acc(
        x.name)).tolist(), columns=["rule", "hit", "acc"])

    data_copy = data.copy()
    data_copy["time_day"] = map(lambda x: stamp2timestr(timestr2stamp(
        x, time_format=time_format), "%Y-%m-%d %H:%M:%S")[:10], data_copy[timestr])
    # 分天的命中量
    time_day = data_copy["time_day"].drop_duplicates().tolist()

    def column_hit_acc_day(day):
        filted = data_copy[data_copy["time_day"] == day]
        return [[day, c, len(filted[filted[c] > 0])] for c in column]

    time_rule_count = pd.DataFrame(list(itertools.chain.from_iterable(map(
        lambda x: column_hit_acc_day(x), time_day))), columns=["time_day", "rule", "hit"])
    return output, time_rule_count


# 日期格式检查
def is_valid_date(data, timestr="time", time_format="%Y-%m-%d %H:%M:%S"):
    """method's help string
    data:传入的dataframe,只支持pandas的dataframe
    timestr:时间的列名，默认 "time"
    time_format:传入的时间格式，默认："%Y-%m-%d %H:%M:%S"。%Y：年，%m：月，%d：日，%H：时，%M：分，%S：秒
            例如：20160829，time_format="%Y%m%d"
                 2016/08/29，time_format="%Y/%m/%d"
                 2016-08-29，time_format="%Y-%m-%d"
                 2016-08-29 00:00:00，time_format="%Y-%m-%d %H:%M:%S"

    """
    result = 0
    for i in range(len(data)):
        try:
            timestr2stamp(str(data.at[i, timestr]), time_format)
        except ValueError:
            print(u"索引为%s的数据时间格式有问题" % (i))
            result += 1
    if result == 0:
        print(u"所有数据日期格式均正确")
        return map(lambda x: timestr2stamp(str(x), time_format), data[timestr])

# poc解析


def poc_analysis(path, is_value=False, weight_dict={}):
    """method's help string
    ------------------------------------------------------------------------------------
    Parameter Description
        path:路径
        is_value:默认 False,返回分数，True时返回指标值
        weight_dict:只在is_value=True时生效。for example,指标名为key，value是w1,w2组成的元组或列表
            {u"7天内多头":(5,1)}
        传入的weight_dict可以不按照顺序,会自动识别命中过的规则列予以计算
    ------------------------------------------------------------------------------------
    Return
        每个样本的每条规则的命中次数或分数
    ------------------------------------------------------------------------------------
    For Example
        from hello_rule_set.rule_tool import *
        applicant_info=poc_analysis("xxx", is_value=False)
    """
    with open(path, "r") as f:
        df = f.read()
    sample_list = df.split("\n")
    if sample_list[-1] == "":
        sample_list = sample_list[:-1]
    # 获取申请人信息
    applicant_info = pd.DataFrame([eval(string)[0]
                                   for string in sample_list if string != "None"])
    applicant_info.columns = [u"提供的申请人信息%s" %
                              (i) for i in range(applicant_info.shape[1])]
    # 获取命中规则以及分数
    applicant_info[["policy_set", "final_score"]] = pd.DataFrame([eval(string)[1] for string in sample_list if (
        (string != "None") and (eval(string)[1] != ""))])[["policy_set", "final_score"]]

    # 提取规则集
    def policy_set_dict(policy_set):
        rule_dict = {}
        if policy_set[0].has_key("hit_rules"):
            for rule in policy_set[0]["hit_rules"]:
                rule_dict[rule["name"]] = rule["score"]
        return rule_dict

    applicant_info["rule_set"] = map(
        lambda x: policy_set_dict(x), applicant_info["policy_set"])
    rule_set = pd.DataFrame(applicant_info["rule_set"].tolist())
    applicant_info[rule_set.columns] = rule_set.fillna(0)
    applicant_info.drop([u"policy_set", u"rule_set"], axis=1, inplace=True)

    if is_value:
        def score2f(x, rule):
            if x == 0:
                return 0
            elif x - weight_dict[rule][0] == 0 and weight_dict[rule][1] == 0:
                return 1
            elif weight_dict[rule][1] > 0:
                return (x - weight_dict[rule][0]) / float(weight_dict[rule][1])
        rule_list = applicant_info.columns.tolist()
        rule_score = []
        [rule_score.append(_) for _ in rule_list if _[:8] != u"提供的申请人信息" and _[
            :8] != "提供的申请人信息" and _ != "final_score"]
        for rule in rule_score:
            applicant_info[rule] = map(
                lambda x: score2f(x, rule.encode("utf8")), applicant_info[rule])
    return applicant_info


def get_weight_df(path):
    weight_df = pd.read_excel(path).fillna("0.0")
    weight_df.drop(weight_df.columns[0], axis=1, inplace=True)
    weight_df.drop(0, axis=0, inplace=True)
    weight_df.columns = ["rule", "weight"]
    weight_df["weight"] = [_.split("*")[0]
                           for _ in weight_df["weight"].tolist()]

    def _split_(_):
        splited = _.split("+")
        try:
            return splited[1]
        except IndexError:
            return 0
    weight_df["w1"] = [_.split("+")[0] for _ in weight_df["weight"].tolist()]
    weight_df["w2"] = [_split_(_) for _ in weight_df["weight"].tolist()]
    weight_df.drop("weight", axis=1, inplace=True)
    weight_df[["w1", "w2"]] = weight_df[["w1", "w2"]].astype("float")
    return weight_df


# path = "/home/yan.wang/桌面/haocheedai_jieguo_dict_save_2017-06-26.txt"
# import json
# print json.dumps(applicant_info["ruledetail"][0], encoding="UTF-8", ensure_ascii=False)

# def rule_detail_analysis(path):
#     with open(path, "r") as f:
#         df = f.read()
#     sample_list = df.split("\n")
#     if sample_list[-1] == "":
#         sample_list = sample_list[:-1]
#
#     applicant_info = pd.DataFrame([eval(sample).values()[0]
#                                    for sample in sample_list if sample != "None"])
