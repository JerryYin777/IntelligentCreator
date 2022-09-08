import json
from django.http import HttpResponse
import time
import os
from decimal import Decimal
from django.shortcuts import render
from .model_base import Model, Trie
from .config import ValidConfig
from transformers import BertTokenizer, GPT2Config
from .utli.gen_title import gen_title
from .utli.wordRank import wordRank
from .utli.sentenceRank import sentenceRank
from .utli.loader import loadStopWords, loadWord2vec
import torch

# import pandas as pd
# from sqlalchemy import create_engine

#
# engine = create_engine("mysql+mysqldb://root:1234@127.0.0.1:3306/news?charset=utf8")

DIR = "./data/"

# 加载模型
config = ValidConfig()
model = Model(GPT2Config.from_json_file(config.bert_config_path))#.to(config.device)
model.load_state_dict(torch.load('./data/model_finetune_200m.pth', map_location='cpu'))
model.to(config.device)
# model.load_state_dict(torch.load('./checkpoint/model_finetune_200m.pth'))
tokenizer = BertTokenizer.from_pretrained(config.vocab_path, use_fast=True)

stopWords = loadStopWords("./data/baidu_stopwords.txt")  # 加载停用词
trie = Trie(stopWords)


# vecMap = loadWord2vec("./data/sgns.weibo.word", wordSet)


# Create your views here.
def index(request):
    return HttpResponse("Hello World!")


# 获取单条新闻文本并返回生成内容
def signal_generate(request):
    news_text = request.POST.get("news_text")
    news_text = news_text.replace("\n", '')
    print(news_text)
    start = time.time()
    '''
    此处写标题生成
    '''
    title = gen_title(model, tokenizer, config, news_text)

    end = time.time()
    generate_time = end - start
    generate_time = str(Decimal(generate_time).quantize(Decimal('0.000')))
    '''
    此处写长摘要生成
    '''
    summary = sentenceRank(news_text, trie)[0][1]
    keyword = wordRank(news_text, trie, windowLen=5, limit=3)
    data = {"title": title, "summary": summary, "keyword": keyword, "time": generate_time}
    data = json.dumps(data)
    # print(type(data))
    return HttpResponse(data)


'''
读取文件批量生成内容 /home/chi/Desktop/train.json
讲生成的文件存入文件夹中
'''

PAGE_SIZE = 5


def batch_generate(request):
    page = request.POST.get("page", "1")
    file_name = request.POST.get("file_name")
    # file_name = eval(file_name)
    print(file_name)
    file = "./data/" + file_name
    # file_name = list(file.split('/'))[-1]
    '''
    读取文件
    '''
    l = file_name.split(".")
    l[0] = l[0] + "_generate."

    file_name = ''.join(l)
    names = os.listdir('data/')
    flag = True
    path = "./data/" + file_name
    try:
        data = json.load(open(path, 'r', encoding='utf-8'))
        start = PAGE_SIZE * (int(page) - 1)
        end = start + PAGE_SIZE
        length = len(data) // 5 + 1
        data = data[start:end]
        return HttpResponse(json.dumps({"code": 200, "message": "success", "data": data, "page_number": length}))
    except:
        file_name_generate = "./data/" + file_name
        print(file_name_generate)
        fw = open(file_name_generate, 'w', encoding='utf-8')

        result = []

        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            k = 1
            for item in data:
                # idx = item['id']
                idx = k
                k += 1
                content = item['content'].replace("\n", '')
                start = time.time()
                '''
                此处写标题生成
                '''
                title = gen_title(model, tokenizer, config, content)
                # title = ""
                end = time.time()
                generate_time = int(end - start)
                generate_time = str(Decimal(generate_time).quantize(Decimal('0.000'))) + "秒"
                summary = sentenceRank(content, trie)[0][1]
                keyWords = wordRank(content, trie, windowLen=5, limit=3)
                '''
                此处写长摘要生成
                '''
                # summary = ''
                a = {"id": idx, "title": title, "summary": summary, "keyword": keyWords, "content": content,
                     "time": generate_time}
                print(a)
                result.append(a)

            # print(result)
            jst = json.dumps(result, ensure_ascii=False)
            # start = time.time()
            fw.write(jst)
            fw.close()
            # end = time.time()
            # length = len(result)
            # df = pd.read_json(file_name_generate, encoding="utf-8", orient='records')
            # df.to_sql(file_name_generate.split('/')[-1], con=engine, if_exists=u'replace', index=False)
            # print(df)
            # data = json.dumps(result)
            print(f"写入时间{end - start}")
            end = -1
            if len(jst) > 5:
                end = 5
            length = len(jst) // 5 + 1
        return HttpResponse(json.dumps({"code": 200, "message": "success", "data": jst[0:end], "page_number": length}))


# 按照文件名打开内容
# def show_generate(request):
#     file_name = request.POST.get("file_name")
#     # # 每页大小
#     # size = int(request.POST.get("size"))
#     # # 当前页数
#     # page = int(request.POST.get("page"))
#     '''
#     对xxx_generate.json文件进行分页操作
#     '''
#     # file_name = file_name.split(".")
#     # file_name[0] = file_name[0] + "_generate."
#     path = "./data/" + ''.join(file_name)
#     # 读取文件数据
#     try:
#         with open(path, "r") as f:
#             data = json.load(f)
#     except:
#         return HttpResponse(json.dumps({"code": 400, "message": "文件读写错误"}))
#     # length = len(data)
#     # page_start = size * (page - 1)
#     # page_end = page_start + size
#     # data = data[page_start:page_end]
#
#     return HttpResponse(json.dumps({"code": 200, "message": "success", "data": data}))


# 展示选择的生成结果
def show_generate(request):
    page = request.POST.get("page", "1")
    file_name = request.POST.get("file_name")
    # file_name = eval(file_name)
    print(file_name)
    file = "./data/" + file_name
    start = PAGE_SIZE * (int(page) - 1)
    end = start + PAGE_SIZE
    with open(file, "r") as f:
        data = json.load(f)
    length = len(data) // 5 + 1
    if length > 5:
        end = 5
    if end > len(data):
        end = -1
    return HttpResponse(json.dumps({"code": 200, "message": "success", "data": data[start:end], "page_number": length}))


# 展示历史生成的结果
def show_generate_files(request):
    file_name = request.POST.get("file_name")
    path = "./data/" + file_name
    names = os.listdir('data/')
    data = []
    for name in names:
        if name.endswith("_generate.json"):
            data.append(name)
    return HttpResponse(json.dumps({"code": 200, "message": "success", "data": data}))


# 展示所有源文件
def show_all_files(request):
    names = os.listdir('data/')
    data = []
    for name in names:
        if "_generate" in name:
            data.append(name)
        else:
            continue
    return HttpResponse(json.dumps({"code": 200, "message": "success", "data": data}))


# 删除文件
def del_file(request):
    file_name = request.POST.get("file_name")
    # 文件所在目录
    path = "./data/"
    # 　os.path.join(path,txt_name0)　获得文件所在路径，并用　os.remove(文件路径)　删除
    try:
        os.remove(os.path.join(path, file_name))
    except:
        return HttpResponse(json.dumps({"code": "200", "message": "出现错误"}))
    return HttpResponse(json.dumps({"code": "200", "message": "删除成功"}))


# 上传文件到服务器
def upload_file(request):
    # 请求方法为POST时，执行文件上传
    print(request.method)
    if request.method == "POST":
        # 获取上传的文件，如果没有文件，就默认为None
        file = request.FILES.get("myfile", None)
        if not file:
            return HttpResponse(json.dumps({"code": "200", "message": "no files for upload"}))
        # 打开特定的文件进行二进制的写操作
        destination = open(os.path.join("./data/", file.name), "wb+")
        # 分块写入文件
        for chunk in file.chunks():
            destination.write(chunk)
        destination.close()
    return HttpResponse(json.dumps({"code": "200", "message": "upload over!"}))
