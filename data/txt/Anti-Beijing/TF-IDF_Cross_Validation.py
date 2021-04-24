#! /usr/bin/env python3

'''
README：
This function takes all txt under current directory as input,
where each txt represents one person's tweets
Then applies TFIDF cross validation,
with each time one person as abstract and the rest as query
result is outputed in a file named output.out
'''


import math
#qry stands for querys and abs stands for abstract
#list _qrys is each person's tweets combined
#dict _total is all the words combined
import glob
#This function inputs all .txt files in the directory and writes them in "lines.txt" with \n\n tp
#with \n\n to separete each file


def map_files(file_list):
    for file in file_list:
        with open(file, 'rt',encoding="utf8") as fd:
            yield fd.read()

def merge_files(file_list, filename):
    with open(filename, 'w',encoding="utf8") as f:
        for line in map_files(file_list):
            f.write("%s\n\n" % line)

def process_file(file_name):
    #This function takes input as filename and returns
    #cran_qry in a way that cran_qry[i] refers to one persons' all words

    cran_obj=open(file_name,"r",encoding="utf8")
    cran_qry_zero=cran_obj.read().split("\n\n")#divide qry by \n\n
    cran_obj.close()

    cran_qry=[x for x in cran_qry_zero if x != "\n"]

    qry_len=len(cran_qry)
    for i in range(0,qry_len):
        cran_qry[i]=cran_qry[i].replace("\n",",")
        # Since we are treating every tweets combined
        cran_qry[i]=cran_qry[i].split(",")#Now cran_qry[i] stores the words of each person
        line_len=len(cran_qry[i])#Length of each person's all words
    return cran_qry

def TF_score(wordsList):
    #takes a list of words and returns a dictionary that contains each words' TF score
    words_len=len(wordsList)
    TF=dict()
    for i in range(0,words_len):
        if wordsList[i] not in TF:
            TF[wordsList[i]]=1
        elif wordsList[i] in TF:
            TF[wordsList[i]]+=1

    for key,value in TF.items():
        TF[key]=value/float(words_len)
    return TF

def IDF_score(tweetsList):
    #takes a list of persons's tweets as input and return a dictionary contains each word's IDF-Score
    tweets_len=len(tweetsList)
    IDF=dict()

    for i in range(0,tweets_len):
        words_len=len(tweetsList[i])
        for j in range(0, words_len):
            The_word=tweetsList[i][j]
            if The_word not in IDF.keys():
                IDF[The_word]=set()
                #There will be no duplicates in set so we can just use it and take length
                IDF[The_word].add(i)

            elif (The_word in IDF.keys()):
                IDF[The_word].add(i)

    for key , value in IDF.items():
        IDF[key]=math.log2(tweets_len/float(len(IDF[key])))
    return IDF

def qry_TFIDF_score(IDF,TF):
    for key, value in TF.items():
        TF[key] = abs(value*IDF[key])
    return TF

def abs_TFIDF_score(IDF,TF):
    for key,value in TF.items():
        if key in IDF.keys():
            TF[key] = abs(value*IDF[key])
        else:
            TF[key] = 0
    return TF

def cosine_score(qry_TFIDF,abs_TFIDF):
    #Now calculate the Cosine similarity
    num=0
    deno_abs=0
    deno_qry=0
    for key,value in abs_TFIDF.items():
        if key in qry_TFIDF.keys():
            num+=qry_TFIDF[key]*abs_TFIDF[key]

    for key,value in abs_TFIDF.items():
        deno_abs+=abs_TFIDF[key]**2
    for key,value in qry_TFIDF.items():
        deno_qry+=qry_TFIDF[key]**2

    deno=math.sqrt(deno_abs)*math.sqrt(deno_qry)
    if deno!=0:
        return num/deno
    else:
        return 0


def cal_average(num):
    sum_num = 0
    for t in num:
        sum_num = sum_num + t

    avg = sum_num / len(num)
    return avg


def main():

    files = glob.glob("*.txt")
    filename = "first_lines.qry"
    output = open("output.out", "w")

    merge_files(files,filename)

    ori_file=process_file(filename)
    ori_len=len(ori_file)
    avg_cos=[None]*ori_len
    #original file, to be cross validated

    for index in range(0,ori_len):
        #cross-validation, take one of the persons out and cross-validates him
        output.write(f"{files[index][:-26]}\n")
        abs=ori_file[index]
        qry=[ori_file[x] for x in range(ori_len) if x != index]

        qry_len = len(qry)
        qry_TFIDF = [None] * qry_len
        qry_IDF = IDF_score(qry)

        for i in range(0, qry_len):
            qry_TFIDF[i] = TF_score(qry[i])
        # print(qry_TFIDF[0])
        for i in range(0, qry_len):
            qry_TFIDF[i] = (qry_TFIDF_score(qry_IDF, qry_TFIDF[i]))

        abs_TF = TF_score(abs)
        abs_TFIDF = abs_TFIDF_score(qry_IDF, abs_TF)
        cos_list = [None] * qry_len

        for i in range(0, qry_len):
            cos_list[i] = cosine_score(qry_TFIDF[i], abs_TFIDF)
            if i>=index:
                j=i+1
            else:
                j=i
            output.write(f"\t{files[index][:-26]}\t{files[j][:-26]}\t")
            output.write("Cos_similarity=%.4f\n" % cos_list[i])
        avg_cos[index]=cal_average(cos_list)
        print(index,"done")
        output.write("Average cosine similarity=%.4f\n\n" % avg_cos[index])
    output.close()





main()
