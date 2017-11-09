#!/usr/bin/python3

# Author : GMFTBY
# Time : 2017.10.19

'''
该模块对于输入的网页特征数据从数据库中抽取并且计算相应的决策树并返回
this model can be changed !
'''

import sys
sys.path.append('..')
import MYSQL.sql as sql    # 导入数据库存储模块
from math import log
import operator
import pprint

def load_data_for_grade(inx = None):
    '''
    该函数从数据库中抽取所有的样本空间数据，将信息规整病返还给监督学习组件去学习
    '''
    save = []
    if inx == None:
        save = sql.main(5)    # 获取全部的样本信息
    else:
        inx.append(0)
        save = [inx]
    print('save' , save)
    # data
    data = []
    for i in save:
        # 数值型变量离散化
        p = []
        # size 离散化
        if 0 <= i[1] < 1000 : p.append(1)
        elif 1000 <= i[1] < 2000 : p.append(2)
        elif 2000 <= i[1] < 3000 : p.append(3)
        elif 3000 <= i[1] < 5000 : p.append(4)
        else : p.append(5)
        # number_reader
        if 0 <= i[2] < 200 : p.append(1)
        elif 200 <= i[2] < 400 : p.append(2)
        elif 400 <= i[2] < 600 : p.append(3)
        elif 600 <= i[2] < 800 : p.append(4)
        elif 800 <= i[2] < 1700 : p.append(5)
        else : p.append(6)
        # number_like
        if i[3] == 0 : p.append(1)
        elif 1 <= i[3] <= 3 : p.append(2)
        else : p.append(3)
        # number_code
        if i[5] == 0 : p.append(1)
        elif 1 <= i[5] <= 3 : p.append(2)
        else : p.append(3)
        # number_photo
        if i[6] == 0 : p.append(1)
        elif 1 <= i[6] <= 2 : p.append(2)
        elif 3 <= i[6] <= 4 : p.append(3)
        else : p.append(4)
        # number_link
        if i[7] == 0 : p.append(1)
        elif 1 <= i[7] <= 3 : p.append(2)
        else : p.append(3)
        # grade --++
        p.append(int(i[4]))
        data.append(p)
    label = ['content size' , 'number_reader' , 'number_like' , 'number_code' , 'number_photo' , 'number_link']
    return data , label

def load_data_for_reader(inx = None):
    '''
    该函数一样使用决策树的代码，只不过改变我们的决策的目标，决策目标更换成对应的阅读量
    '''
    save = []
    if inx == None : save = sql.main(5)
    else:
        save = [inx]
        print(save)
    data = []
    for i in save:
        p = []
        # size 离散化
        if 0 <= i[1] < 1000 : p.append(1)
        elif 1000 <= i[1] < 5000 : p.append(2)
        else : p.append(3)
        # number_like
        if i[3] == 0 : p.append(1)
        elif 1 <= i[3] < 5 : p.append(2)
        else : p.append(3)
        # grade
        if 0 <= i[4] < 60 : p.append(1)
        elif 60 <= i[4] < 80 : p.append(2)
        else : p.append(3)
        # number_code
        if i[5] == 0 : p.append(1)
        elif 1 <= i[5] <= 3 : p.append(2)
        else : p.append(3)
        # number_photo
        if i[6] == 0 : p.append(1)
        elif 1 <= i[6] <= 3 : p.append(2)
        else : p.append(3)
        # number_link
        if i[7] == 0 : p.append(1)
        elif 1 <= i[7] <= 3 : p.append(2)
        else : p.append(3)
        # number_reader
        if 0 <= i[2] < 500 : p.append(1)
        elif 500 <= i[2] < 1000 : p.append(2)
        else : p.append(3)
        data.append(p)
    label = ['content size' , 'number_reader' , 'number_like' , 'number_code' , 'number_photo' , 'number_link']
    return data , label

def calShannoneEnt(dataset):
    '''
    该函数计算香农熵
    '''
    length = len(dataset)
    label = {}
    for i in dataset:
        currentlabel = i[-1]
        if currentlabel not in label.keys():
            label[currentlabel] = 0
        label[currentlabel] += 1
    shannonEnt = 0.0
    for key in label:
        p = float(label[key]) / length
        shannonEnt -= p * log(p , 2)
    return shannonEnt

def splitdataset(dataset , axis , value):
    '''
    该函数用来根据 data[axis] = value 划分数据集
    '''
    ret = []
    for i in dataset:
        if i[axis] == value:
            p = i[:axis]
            p.extend(i[axis + 1 :])
            ret.append(p)
    return ret

def choosebestfeaturetosplit(dataset):
    '''
    该函数遍历所有的特征，试图在本次的询问中找到最合适的特征进行分支的划分
    '''
    numfeature = len(dataset[0]) - 1
    # 初始化基础的信息熵，信息增益和最优的选择
    baseentroy = calShannoneEnt(dataset)
    baseinfogain = 0.0
    bestfeature = -1
    for i in range(numfeature):
        fealist = [example[i] for example in dataset]
        uniquevals = set(fealist)    # 找到dataset数据集在i特征上的值分布
        newentroy = 0
        for value in uniquevals:
            subdataset = splitdataset(dataset , i , value)    # 分支i的子集
            p = len(subdataset) / float(len(dataset))    # 分支i的总量概率
            newentroy += p * calShannoneEnt(subdataset)    # 概率信息增益
        infogain = baseentroy - newentroy    # 只要infogain越大代表选择越好
        if infogain > baseinfogain :
            baseinfogain = infogain
            bestfeature = i
    return bestfeature

def major(data):
    '''
    当组内的标签用完了还是没有完全的划分好我们的子集样本的时候，我们需要多数选择机制(标签)
    '''
    classcount = {}
    for i in data:
        if i not in classcount.keys():
            classcount[i] = 0
        classcount[i] += 1
    save = sorted(classcount.items() , key = operator.itemgetter(1) , reverse = True)
    return save[0][0]

def createtree(dataset , label):
    '''
    该函数递归构建 ID3 决策树
    '''
    classlist = [example[-1] for example in dataset]    # 子集的标签列表
    if classlist.count(classlist[0]) == len(classlist):
        # 子集样本同一特征
        return classlist[0]
    if len(dataset[0]) == 1:
        # 子集没有可供筛选询问的特征,多数返回
        return major(classlist)
    bestfeature = choosebestfeaturetosplit(dataset)    # 按照香农熵计算信息增益选择最合适的分类特征
    bestfeaturelabel = label[bestfeature]    # 获取特征的名称
    tree = {bestfeaturelabel : {}}    # 构建树
    del label[bestfeature]
    featurevalues = [example[bestfeature] for example in dataset]
    uniquevalue = set(featurevalues)    # 该最好特征值域别
    for value in uniquevalue:
        sublabel = label[:]
        tree[bestfeaturelabel][value] = createtree(splitdataset(dataset , bestfeature , value) , sublabel)
    return tree

def classify(tree , label , test):
    '''
    使用决策树决策的函数
    '''
    feature = list(tree.keys())[0]
    subtree = tree[feature]
    index = label.index(feature)
    true_label = None
    for i in subtree.keys():
        if test[index] == i:
            if type(subtree[i]).__name__ == 'dict':
                true_label = classify(subtree[i] , label , test)
            else:
                true_label = subtree[i]
            break
    return true_label

def save_model_to_sql(model):
    '''
    该函数将产生的字典型决策树模型存储在数据库的user表中
    '''
    import pickle
    with open('../MYSQL/model.pkl' , 'wb') as f:
        pickle.dump(model , f)
    print('模型文件存放在../MYSQL/model.pkl中')

def get_model_from_sql():
    '''
    该函数将存储在数据库中的决策树模型提取出来
    '''
    import pickle
    with open('../MYSQL/model.pkl' , 'rb') as f:
        model = pickle.load(f)
    return model

def analyse(res):
    # res is a list of dict
    model = get_model_from_sql()
    for i in res:
        new = load_data_for_grade([0 , i['size'] , i['number_reader'] , i['number_like'] , 0 , i['number_code'] , i['number_photo'] , i['number_link']])[0][0][:-1]
        p = classify(model , ['content size', 'number_reader', 'number_like', 'number_code', 'number_photo', 'number_link'] , new)
        if p != None : i['grade'] = p
        else : 
            i['grade'] = 0
            print('error')
    return res

if __name__ == "__main__":
    '''
    dataset , label = load_data_for_grade(None)
    plabel = label.copy()
    model = createtree(dataset , plabel)
    save_model_to_sql(model)
    print(model)

    # 检测正确率
    number = 0
    nonenumber = 0
    for i in dataset:
        res = classify(model , label , i[:-1])
        if res == None : nonenumber += 1
        elif res == i[-1]:
            number += 1
    print(len(dataset) , nonenumber , number)
    print(number * 1.0 / len(dataset))
    '''
    # a = analyse([{'size':11140 , 'number_reader':562,'number_like':0,'number_code':16,'number_photo':24,'number_link':2}])
    load_data_for_reader([0 , 4007,0, 4, 4 ,3, 2,0])
