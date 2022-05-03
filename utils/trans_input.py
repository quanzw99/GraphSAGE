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


def encode_id(raw_list):
    # 对raw_list进行去重后
    # 按照int(raw_name)后的大小排序
    # 并按顺序编号id
    raw_list = list(set(raw_list))
    raw_list.sort(key=lambda item_name: int(item_name))
    id_map = {}
    id_index = 0
    for node in raw_list:
        id_map[node] = id_index
        id_index = id_index + 1
    return id_map


def trans_one_hot(cur_id, list_len):
    one_hot = [0] * list_len
    one_hot[cur_id] = 1
    return one_hot


def trans_id_map(id_map_file, node_list):
    id_map = encode_id(node_list)

    # 写入json文件
    with open(id_map_file, "w") as fp:
        json.dump(id_map, fp)
    print("Done transforming id_map..")
    return id_map


def trans_class_map(class_map_file, class_map, label_list):
    label_map = encode_id(label_list)
    class_map_len = len(label_map)

    # 遍历class_map将id转换为one_hot向量
    for key, value in class_map.items():
        class_map[key] = trans_one_hot(label_map[value], class_map_len)

    # 写入json文件
    with open(class_map_file, "w") as fp:
        json.dump(class_map, fp)
    print("Done transforming class_map..")


def trans_G(G_file, id_map, links_list):
    graph_data = {}

    # G文件包括5个key: directed、graph、nodes、links、multigraph
    # 这里是按PPI数据给的一些初始值，后续可根据需求进行更改
    graph_data["directed"] = False
    graph_data["graph"] = {}

    # 将所有节点信息存储为包含test id val 的dict
    # 所有test val 都设置为False
    nodes = []
    for key, value in id_map.items():
        nodes.append({"test": False, "id": value, "val": False})
    graph_data["nodes"] = nodes

    # links_list中实际也存储了包含source target的键值对
    # 这里需要从node_name 转换到node_id
    links = []
    for link in links_list:
        links.append({"source": id_map[link["source"]], "target": id_map[link["target"]]})
    graph_data["links"] = links

    graph_data["multigraph"] = False

    # 写入json文件
    with open(G_file, "w") as fp:
        json.dump(graph_data, fp)
    print("Done transforming G..")


def trans_input(dataset_file, n2l_file, dataset_name):

    # 创建输出目录
    print_dir = "../" + dataset_name + "/";
    if not os.path.exists(print_dir):
        os.makedirs(print_dir)

    # 计算各个文件路径
    G_file = print_dir + dataset_name + "-G.json"
    id_map_file = print_dir + dataset_name + "-id_map.json"
    class_map_file = print_dir + dataset_name + "-class_map.json"

    # 读取交互信息
    node_list = []
    links_list = []
    with open(dataset_file, "r") as reader:
        for line in reader:
            parts = line.strip().split()
            # s_name means source name, t_name means target name
            s_name, t_name = parts[0], parts[1]
            node_list.append(s_name)
            node_list.append(t_name)
            # 实际交互存为双向的
            links_list.append({"source": s_name, "target": t_name})
            # links_list.append({"source": t_name, "target": s_name})


    # 完成id_map转换
    id_map = trans_id_map(id_map_file, node_list)

    # 读取node2label文件信息
    label_list = []
    class_map = {}
    with open(n2l_file, "r") as reader:
        for line in reader:
            parts = line.strip().split()
            node_name, label_name = parts[0], parts[1]
            class_map[node_name] = label_name
            label_list.append(label_name)

    # 完成class_map转换
    trans_class_map(class_map_file, class_map, label_list)

    # 完成G文件转换
    trans_G(G_file, id_map, links_list)


if __name__ == '__main__':

    parser = ArgumentParser(description="Transform input from raw data.")
    parser.add_argument("dataset_dir", help="Path to directory of the raw dataset.")
    parser.add_argument("dataset_name", help="Name of the raw dataset.")
    args = parser.parse_args()
    dataset_dir  = args.dataset_dir
    dataset_name = args.dataset_name
    dataset_file = dataset_dir + dataset_name + "/" + dataset_name + ".txt"
    n2l_file = dataset_dir + dataset_name + "/node2label.txt"

    print("Transforming input data..")
    trans_input(dataset_file, n2l_file, dataset_name)
    print("Done transforming input data..")