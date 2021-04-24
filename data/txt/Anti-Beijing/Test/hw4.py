#! /usr/bin/env python3

from math import log, sqrt
from re import split

abstract_file_name = "cran.all.1400"
quiry_file_name = "cran.qry"
out_file_name = "output.txt"

ABS_CNT = 1400
QRY_CNT = 225






def isvalidword(s: str) -> bool:
    if (len(s)<2) or (not s.isalpha()) or (s[-2:]=='ly') or (s in stop_words):
        return False
    else:
        return True


def transform(word: str) -> str:
    if len(word)>4:
        if word.endswith("ing"):
            word = word[0:-3]
        elif word.endswith("ed") or word.endswith("ly"):
            word = word[0:-2]
        elif word.endswith("s"):
            word = word[0:-1]
    return word


def cosine(A: dict, B: dict) -> float:
    if len(A)==0 or len(B)==0:
        return 0
    numerator = 0
    for word in A:
        if word in B:
            numerator += A[word] * B[word]
    denom_A = 0
    for word in A:
        denom_A += (A[word] ** 2)
    denom_B = 0
    for word in B:
        denom_B += (B[word] ** 2)
    return numerator / sqrt(denom_A) / sqrt(denom_B)


def get_idf(doc_instance: dict) -> dict:
    idf = {}
    for word in doc_instance:
        idf[word] = log( ABS_CNT / doc_instance[word])
        try:
            assert idf[word] >= 0
        except:
            print('There are {} documents. But "{}" appears {} times.'\
                .format(ABS_CNT, word, doc_instance[word]))
            exit()
    return idf


def get_tf(doc_file_name: str, expected_cnt: int) -> list:
    term_freq = [] # term frequency in each document
    with open(doc_file_name, 'r') as f_doc:
        i = 0
        reading_doc = False
        for line in f_doc:
            if len(line)<2:
                pass
            elif line[0:2] == '.I': # new document started
                # add new doc
                term_freq.append({})
                reading_doc = False
                i += 1
            elif reading_doc:
                try:
                    words = split(" |-|/|=|\'|\\\|\\.|,|\(|\)|:", line.rstrip(' \n\r'))
                    for word in words:
                        word = transform(word)
                        if isvalidword(word):
                            term_freq[-1][word] = term_freq[-1].get(word, 0) + 1
                except:
                    print("Error spliting doc# {}: {}".format(i, line))
                    exit()
            elif line[0:2] == '.W':
                reading_doc = True
            else:
                pass
        else: # dealing with the last document
            try:
                assert reading_doc==True
            except:
                print("The last document is corrupt.")
                exit()
            else:
                reading_doc = False
    try:
        assert len(term_freq)==expected_cnt
    except:
        print("Expected {} docs, but {} read.".format(expected_cnt, len(term_freq)))
        exit()
    else:
        return term_freq


def get_tfidf(term_freq: list, idf: dict) -> list:
    doc_tfidf = []
    for doc_tf in term_freq:
        vec = {}
        for word in doc_tf:
            vec[word] = doc_tf[word] * idf.get(word, log(ABS_CNT))
        doc_tfidf.append(vec)
    return doc_tfidf


def main():
    # Read abstracts
    term_freq = get_tf(abstract_file_name, ABS_CNT)

    # Count number of instances 
    doc_instance = {} # number of doc containing key
    for doc in term_freq:
        for word in doc:
            doc_instance[word] = doc_instance.get(word, 0) + 1

    # Generate IDF
    idf = get_idf(doc_instance)
    doc_instance.clear()

    # Generate TF-IDF for abstracts
    abstract_tfidf = get_tfidf(term_freq, idf)
    term_freq.clear()

    # Read the quiries
    term_freq = get_tf(quiry_file_name, QRY_CNT)

    # Generate TF-IDF for quiries
    quiry_tfidf = get_tfidf(term_freq, idf)
    term_freq.clear()
    idf.clear()

    # Generate output
    with open(out_file_name, 'w') as f_out:
        for i in range(QRY_CNT):
            # calculate similarities
            similarity = {}
            for j in range(ABS_CNT):
                similarity[j] = cosine(quiry_tfidf[i], abstract_tfidf[j])
            # rank similarities
            itemls=sorted(list(similarity.items()),key=lambda x:x[1], reverse=True)
            similarity.clear()
            # print
            for item in itemls:
                j, value = item
                f_out.write("{} {} {}\n".format(i+1, j+1, value))


main()
