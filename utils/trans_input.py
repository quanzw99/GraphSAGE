# /usr/bin/env python
# -*- coding: UTF-8 -*-
# 为降低于原项目的耦合，trans_input.py用于将现有数据（交互信息、node2label）转换为
# 与example_data一致的、能被原项目直接读取的-G、-class_map、-id_map文件
# 使用命令 $1 = dataset_dir，$2 = dataset_name
# e.g. python utils/trans_input.py ../raw_data/ dblp
# 处理后的数据输出在项目根目录下，文件夹与dataset_name同名

import json
import os
from argparse import ArgumentParser

def trans_input(dataset_file, n2l_file, dataset_name):

    # 创建输出目录
    print_dir = "../" + dataset_name + "/";
    if not os.path.exists(print_dir):
        os.makedirs(print_dir)

    # 计算各个文件路径
    G_file = print_dir + dataset_name + "-G.json"
    id_map_file = print_dir + dataset_name + "-id_map.json"
    class_map_file = print_dir + dataset_name + "-class_map.json"

    nodelist = []
    with open(dataset_file, "r") as reader:
        for line in reader:
            parts = line.strip().split()

            # sid means source id, tid means target id
            sid, tid = parts[0], parts[1]
            nodelist.append(sid)
            nodelist.append(tid)


    # 去重后按照int(string)后的大小排序
    # 并按顺序编号id
    nodelist = list(set(nodelist))
    nodelist.sort(key=lambda node: int(node))
    id_map = {}
    id_index = 0
    for node in nodelist:
        id_map[node] = id_index
        id_index = id_index + 1

    print(id_map_file)
    # 写入json文件
    with open(id_map_file, "w") as fp:
        json.dump(id_map, fp)


if __name__ == '__main__':

    parser = ArgumentParser(description="Transform input from raw data.")
    parser.add_argument("dataset_dir", help="Path to directory of the raw dataset.")
    parser.add_argument("dataset_name", help="Name of the raw dataset.")
    args = parser.parse_args()
    dataset_dir  = args.dataset_dir
    dataset_name = args.dataset_name
    dataset_file = dataset_dir + dataset_name + "/" + dataset_name + ".txt"
    n2l_file = dataset_dir + dataset_name + "/node2label.txt"

    trans_input(dataset_file, n2l_file, dataset_name)