#!/usr/bin/python3

'''该模块使用K临近算法计算我们的文本的预计影响(阅读的读者数目)'''

import sys
sys.path.append('..')
import MYSQL.sql as sql
import numpy as np
import operator

def classify(dataset , test , label , k):
    # 归一化
    dis = []
    for index , i in enumerate(dataset):
        disp = (abs((test[0] - i[0]) * 0.0006) + (test[1] - i[1])**2 * 0.5 + (test[2] - i[2])**2 * 0.5 + (test[3] - i[3])**2 * 0.4 + (test[4] - i[4])**2 * 0.3 + (test[5] - i[5])**2 * 0.3) * 0.5
        dis.append((disp, label[index]))
    dis.sort(key = operator.itemgetter(0))
    sump = 0
    print(dis[:k])
    for i in dis[:k]:
        sump += i[1]
    return sump * 1.0 / k

def main(ans):
    k = 20    # 默认只有10个
    data = sql.main(5)
    test = []
    label = []
    for i in data:
        p = []
        p.append(i[1])
        p.extend(i[3:])
        test.append(p)
        label.append(i[2])
    ansp = [ans['size'] , ans['number_like'] , ans['grade'] , ans['number_code'] , ans['number_photo'] , ans['number_link']]
    return classify(np.array(test)   , ansp , label , k)

if __name__ == '__main__':
    main({'md5url': 'b4d110b310c51bbb72c1e3db58dd6786', 'size': 4007, 'number_like': 4, 'number_reader':1969, 'number_code': 3, 'number_photo': 2, 'number_link': 0, 'blog_name': 'Euler Graph - 欧拉图 │详解 - CSDN博客' , 'grade':4})

