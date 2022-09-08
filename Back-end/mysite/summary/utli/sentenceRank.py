import re
import jieba
import math
import numpy as np

from summary.utli.loader import loadWord2vec


def generateMap(sentList):
    """
    对于一个分句结果，生成句子到id的字典
    :param wordList: 分句后的句列表
    :return: sent2Id, id2Sent
    """
    sent2Id, id2Sent = {}, {}
    for sent in sentList:
        value = len(sent2Id)
        sent2Id[sent] = value
        id2Sent[value] = sent
    return sent2Id, id2Sent


def sentWord2vec(sent, vecMap):
    """
    对于一个句子，生成其句向量表示
    :param sent: 句子的分词结果
    :param vecMap: 词向量词典
    :return: 一个300维的句向量表示
    """
    vec = [0.0 for i in range(300)]
    if len(sent) == 0:
        return vec

    for word in sent:
        wordVec = [0.0 for i in range(300)]
        if word in vecMap.keys():
            wordVec = vecMap[word]
        for i in range(300):
            vec[i] += wordVec[i]
    for i in range(300):
        vec[i] /= len(sent)
    return vec


def similarity(sent1, sent2, vecMap):
    """
    计算两个分词后句子的相似度
    :param sent1: 句子1
    :param sent2: 句子2
    :param vecMap: 词向量词典
    :return: 两个句子的相似度
    """
    if len(sent1) == 0 or len(sent2) == 0:
        return 0.0
    sent1 = sentWord2vec(sent1, vecMap)
    sent2 = sentWord2vec(sent2, vecMap)

    vec1 = np.array(sent1)
    vec2 = np.array(sent2)
    f = np.sum(vec1 * vec2)
    p = np.sqrt(sum(vec1 ** 2))
    r = np.sqrt(sum(vec2 ** 2))
    return f / (p * r)


def generateTrans(sentList, sent2Id, vecMap):
    """
    生成转移转移矩阵
    :param wordList: 句子分词后的词列表
    :param word2Id: 从词转向id的字典
    :param vecMap: 词向量词典
    :return: 标准化的转移矩阵
    """

    n = len(sent2Id)

    trans = [[0.0 for i in range(n)] for j in range(n)]

    for i in range(n):
        for j in range(i + 1, n):
            value = similarity(sentList[i], sentList[j], vecMap)
            trans[i][j] = trans[j][i] = value

    for i in range(n):
        sumt = sum(trans[i])
        if sumt == 0:
            continue
        for j in range(n):
            trans[i][j] /= sumt

    return trans


def calculateRank(trans, iteration=1000):
    """
    计算rank向量
    :param trans: 转移概率矩阵
    :param iteration: 迭代次数，默认1000次（收敛则立即返回）
    :return: rank向量
    """
    n = len(trans)
    if n == 0:
        return []
    d = 0.85
    rank = [1 / n for _ in range(n)]
    for ite in range(iteration):
        rank_n = [0.0 for _ in range(n)]
        for i in range(n):
            for j in range(n):
                rank_n[i] += trans[j][i] * rank[j]
            rank_n[i] = 1 - d + d * rank_n[i]
        rank = rank_n

        norm = math.sqrt(sum(x * x for x in rank))
        norm_n = math.sqrt(sum(x * x for x in rank_n))
        if abs(norm - norm_n) < 0.01:  # 计算二范数 判断收敛
            break

    return rank


def sentenceRank(paragraph, trie, limit=3):
    """
    给定一篇文章，计算该文章中的前limit个句子
    :param paragraph: 待计算文章
    :param trie: trie树
    :param limit: 前limit个句子，默认为3（但limit大于全部句子个数时，返回全部句子）
    :return: 前limit个句子，以[(score, sent1), (score, sent2), (score, sent3)...]的形式返回
    """
    sentences = re.split(r'。|！|\!|\.|？|\?', paragraph)
    sent2Id, id2Sent = generateMap(sentences)

    for i in range(len(sentences)):
        sentences[i] = [word for word in jieba.cut(sentences[i])]
    newSent = []
    for i in range(len(sentences)):
        sent = []
        for w in sentences[i]:
            if trie.isExist(w) == False:
                sent.append(w)
        newSent.append(sent)

    wordSet = []
    for sent in newSent:
        for word in sent:
            if word not in wordSet:
                wordSet.append(word)

    vecMap = loadWord2vec("./data/sgns.weibo.word", wordSet)
    trans = generateTrans(newSent, sent2Id, vecMap)
    rank = calculateRank(trans)

    for i in range(len(rank)):
        rank[i] = (rank[i], id2Sent[i])

    rank.sort(key=lambda s: (s[0]), reverse=True)

    return rank[0: min(len(rank), limit)]

