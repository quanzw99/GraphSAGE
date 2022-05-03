# /usr/bin/env python
# -*- coding: UTF-8 -*-
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from scipy.sparse import lil_matrix
import numpy as np
import json


def format_training_data_for_dnrl(emb_file, i2l_file):
    i2l = dict()
    with open(i2l_file, 'r') as reader:
        for line in reader:
            parts = line.strip().split()
            n_id, l_id = int(parts[0]), int(parts[1])
            i2l[n_id] = l_id
    '''
    emb_file对应emb文件夹下每次生成的embedding文件，i2l_file对应data文件夹下的node2label
    对文件读取的每一行按空格进行分隔成两部分，分别是nid和lid
    对字典i2l，nid为key，指node_id，lid为value，指label_id
    '''
    i2e = dict()
    with open(emb_file, 'r') as reader:
        reader.readline()
        for line in reader:
            embeds = np.fromstring(line.strip(), dtype=float, sep=' ')
            node_id = embeds[0]
            if node_id in i2l:
                i2e[node_id] = embeds[1:]
    '''
    fromstring(string, dtype=None, count=-1, sep='')
    string对应需处理字符串，dtype对应需转换类型，默认为float64
    count对应需处理字符串长度，默认为-1，设置几位就处理输入字符串的前几位，-1对应全部
    sep一般情况下都按ascii码解析，此处sep=' '，应该是将空格前后划分为两个数进行转换

    strip()函数对字符串首尾的空格进行删除，那么就只剩中间的空格
    将一行嵌入按照空格划分开后，最终embeds的形式应该是具有多个值的的向量
    '''
    Y = []
    X = []
    i2l_list = sorted(i2l.items(), key=lambda x: x[0])
    for (the_id, label) in i2l_list:
        Y.append(label)
        X.append(i2e[the_id])

    X = np.stack(X)
    return X, Y
    '''
    sorted(iterable, key=None, reverse=False)  
    方法返回的是一个新的列表，而非在原来基础上进行的操作
    iterable为可迭代对象；reverse为排序规则，True降序，False升序
    key为用来比较的元素，即指定可迭代对象中的元素来进行排序

    items()以列表形式返回可遍历的（键，值）元组数组
    lambda x: x[0] 即按照第0维排序，也就是事实上的第一维，x在此时代指可迭代对象

    numpy.stack(arrays, axis=0)
    沿着指定维度对数据进行连接，axis=0即第一维度
    此处就是将X中的元素全部合并到一起
    '''


def lr_classification(X, Y, cv):
    # clf = KNeighborsClassifier()
    clf = LogisticRegression()
    scores_1 = cross_val_score(clf, X, Y, cv=cv, scoring='f1_micro', n_jobs=8)
    scores_2 = cross_val_score(clf, X, Y, cv=cv, scoring='f1_weighted', n_jobs=8)
    scores_1 = scores_1.sum() / 5
    scores_2 = scores_2.sum() / 5
    return scores_1, scores_2
    '''
    LogisticRegression()为逻辑回归，公式为1 / (1 + e ^ -z)

    模型训练过程中，采用K折交叉验证，一般会用到sklearn.model_selection的cross_val_score方法
    clf为数据对象；X和Y分别为数据和预测数据；cv为交叉验证生成器或可迭代的次数
    scoring为调用的方法；n_jobs为同时工作的cpu个数
    '''


if __name__ == '__main__':
    X, Y = format_training_data_for_dnrl('../unsup-dblp/graphsage_mean_small_0.000010/val.txt', '../raw_data/dblp/node2label.txt')
    accuracy_score, weighted_score = lr_classification(X, Y, cv=5)
    print(accuracy_score)
    print(weighted_score)
