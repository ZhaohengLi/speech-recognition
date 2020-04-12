import gensim
import jieba
import numpy

model = gensim.models.KeyedVectors.load_word2vec_format('./vector/sgns.weibo.bigram-char', binary=False)


def sentence_vector(s):
    words = jieba.lcut(s)
    v = numpy.zeros(300)
    word_count = 0
    for word in words:
        if word in model:
            word_count += 1
            v += model[word]
    if word_count == 0:
        return numpy.zeros(300)
    else:
        v /= word_count
        return v


def sentence_distance(sentence1, sentence2):
    vec1 = sentence_vector(sentence1)
    vec2 = sentence_vector(sentence2)
    similarity = numpy.dot(vec1, vec2) / (numpy.linalg.norm(vec1) * numpy.linalg.norm(vec2))
    return similarity
