import os
import re


class get_rule_set(object):
    """docstring for get_rule_set
    data:feature data
    path:dot file path for decisiontree 
    node_black_num:node be select if black sample num of this node
    ratio_accuracy:select accuracy for you want,
                    The greater the accuracy rate of ratio_accuracy,
                    and when you have a big ratio_accuracy,you should 
                    setting a small node_black_num,and vice versa.
    sequenceId:column which sequenceId that name of you data
    label:column which label that name of you data

    # example
    if __name__=="__main__":
        import pandas as pd
        data=pd.read_csv("label_index.csv")
        del data["Unnamed: 0"]
        data=sqlContext.createDataFrame(data)
        new=get_rule_set(data,"tree/",ratio_accuracy=0.9,ratio_recall=0.3,sequenceId="sequence_mob")
        # dot_list=new.get_dot_list("tree2.dot",2)
        sql,rule=new.get_sql_and_rule()
        output=new.get_data()
    """

    def __init__(self, data, path, node_black_num, ratio_accuracy=0.9, sequenceId="sequenceId", label="label"):
        super(get_rule_set, self).__init__()
        self.data = data
        self.path = path
        self.node_black_num = node_black_num
        self.ratio_accuracy = ratio_accuracy
        self.sequenceId = sequenceId
        self.label = label

    def get_dot_list(self, file, k):
        """method's help string.
        file:dot file 
        k:number of tree
        """
        whole_1 = []
        with open(self.path + file, 'r') as f:
            dy = f.read()
            # print f.read()

        dy = dy.replace('labelangle', '').replace('labeldistance', '').replace('headlabel', '')
        tree_a = dy.split(';')
        tree_c = []
        tree_b = []
        # 筛选数据
        for i in range(len(tree_a)):
            if len(tree_a[i]) < 40:
                tree_c.append(tree_a[i])
            else:
                tree_b.append(tree_a[i])

        for i in range(len(tree_c)):
            tree_c[i] = tree_c[i].split('->')
            if len(tree_c[i]) > 1:
                tree_c[i][1] = tree_c[i][1][1:4].replace('[', '')
                if len(tree_c[i][0]) == 5:
                    tree_c[i][0] = tree_c[i][0][0:4]

        len_max = 0
        len_min = 9999
        for i in range(len(tree_b) - 1):
            len1 = len(tree_b[i])
            # print i ,len1
            if len1 > len_max:
                len_max = len1
            else:
                len_max = len_max
            if len1 < len_min:
                len_min = len1
            else:
                len_min = len_min
        # print len_max,len_min

        tree_b_transition = []
        tree_b_end = []
        for i in range(len(tree_b)):
            if len(tree_b[i]) > (len_min + 15):
                tree_b_transition.append(tree_b[i])
            else:
                tree_b_end.append(tree_b[i])

        def f1(tree):
            for i in range(len(tree)):
                tree[i] = tree[i].split('[l')
                tree[i][0] = tree[i][0][0:4]
            return tree
        tree_b_transition = f1(tree_b_transition)
        tree_b_end = f1(tree_b_end)

        for i in range(len(tree_b_end)):
            tree_b_end[i][1] = tree_b_end[i][1].split(',')
            tree_b_end[i][1][0] = tree_b_end[i][1][0].split('[')
            tree_b_end[i][1][1] = tree_b_end[i][1][1].split(']')

        for i in range(len(tree_b_transition)):
            tree_b_transition[i][1] = tree_b_transition[i][1].split('<=')

        def f2(date):
            rule = []
            while int(date) != 0:
                for j in range(1, len(tree_c) - 1):
                    if int(tree_c[j][1]) == int(date):
                        for k in range(len(tree_b_transition)):
                            if tree_c[j][0] == tree_b_transition[k][0]:
                                name = tree_b_transition[k][1][0][6:-1]
                                label = tree_b_transition[k][1][1][1:6]
                                # print tree_c[j][0],name,label
                                i = []
                                for h in range(1, len(tree_c) - 1):
                                    if int(tree_c[h][0]) == int(tree_c[j][0]):
                                        i.append([tree_c[h][0], tree_c[h][1]])
                                # print i , tree_c[j][1]
                                if i[0][1] == tree_c[j][1]:
                                    sign = '<='
                                else:
                                    sign = '>'
                                date = date.replace('\n', '')
                                label = label.replace('\\n', '')
                                a = tree_c[j][0]
                                a = a.replace('\n', '')
                                rule.append([date + '<----' + a, name, sign, label])
                                date = tree_c[j][0]
            return rule

        for i in range(len(tree_b_end)):
            if tree_b_end[i][1][1][1][-1:] == '1':  # 黑样本为1，白样本为0
                # print i,tree_b_end[i][1][1][0],tree_b_end[i][1][0][1]
                sample = float(tree_b_end[i][1][0][0].split('\\')[1].split('=')[1])
                black_num = float(tree_b_end[i][1][1][0])
                white_num = float(tree_b_end[i][1][0][1])
                ratio_0 = black_num / (black_num + white_num)
                ratio_1 = (ratio_0 * sample)

                if ((ratio_0 >= self.ratio_accuracy) & (ratio_1 > self.node_black_num)):  # ratio以及3为筛选阈值
                    # print tree_b_end[i][1][1][0],ratio
                    num = f2(tree_b_end[i][0])
                    # print num
                    whole_1.append([k, num])
        return whole_1

    def get_sql_and_rule(self):
        """method's help string.
        this method return sql and rule details,
        sql is use of get_data,rule can help you know which rules are selected 
        """
        self.data.registerTempTable("data")
        str_all = """select %s,%s,""" % (self.sequenceId, self.label)

        rule = []
        dirs = os.listdir(self.path)
        for file in dirs:
            p = re.compile('\d+')
            try:
                k = p.findall(file)[0]
            except IndexError:
                print u"正则表达式索引错误，请检查文件名格式，以及get_sql函数"
            file_name = file.split('.')[0]
            dot_list = self.get_dot_list(file, k)
            for i in range(len(dot_list)):
                str1 = ''
                one_list = dot_list[i][1]
                for j in range(len(one_list)):
                    one_rule = one_list[j]
                    str1 += one_rule[1]
                    str1 += one_rule[2]
                    str1 += one_rule[3].replace("\\", "")
                    if j < len(one_list) - 1:
                        str1 += ' and '
                    rule.append([k, i, (one_rule[1] + '  ' + one_rule[2] + '  ' + one_rule[3]).replace("\\", "")])
                str_2 = """(case when """ + str1 + """ then 1 else 0 end) as %s_rule%s,""" % (file_name, i)
                str_all += str_2
        str_all = str_all[:len(str_all) - 1]
        str_all += """ from data """
        return str_all, pd.DataFrame(rule, columns=["tree", "rule", "details"])

    def get_data(self):
        """method's help string.
        get which sample hited by which rlue_set 
        """
        sql, rule = self.get_sql_and_rule()
        output = sqlContext.sql(sql).toPandas()
        # num_count=[]
        # [num_count.append(output.iloc[i,1:-1].sum()) for i in output.index]
        # output["num_count"]=num_count
        sqlContext.dropTempTable("data")
        return output
