def loadStopWords(path):
    file = open(path, mode="r", encoding="utf-8")
    res = []
    for line in file:
        line = line.strip()
        line = line.strip('\n')
        res.append(line)
    return res


def loadWord2vec(path, wordSet):
    file = open(path, mode="r", encoding="utf-8")
    res = {}
    for line in file:
        line = line.strip()
        line = line.strip('\n')
        line = line.split(' ')

        word = line[0]

        if word in wordSet:
            vec = [float(x) for x in line[1:]]
            res[word] = vec

    return res
