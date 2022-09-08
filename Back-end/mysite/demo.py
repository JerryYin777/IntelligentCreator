import json

import pandas as pd

# df = pd.read_json("data/train_generate.json", encoding="utf-8", orient='records')
# print(df)
# data = json.loads('data/train_generate.json')
# print(data)
# 数据路径
path = "data/dev.json"
# 读取文件数据
# with open(path, "r") as f:
#     data = json.load(f)
# 读取每一条json数据
# print(len(data[0:5]))

data = json.load(open(path, 'r', encoding='utf-8'))
del data
print(data)
# import os
# names = os.listdir('data/')
# for i in names:
#
# print(names)
# a = "hello.json"
# a = a.split('.')
# print(a)