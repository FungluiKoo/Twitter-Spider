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
import pathlib

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

def process_file(file_name : str)->list:
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

def TF_score(wordsList :list) -> dict:
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

def IDF_score(tweetsList:list)->dict:
    #takes a list of many persons's tweets as input and return a dictionary contains each word's IDF-Score
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

def qry_TFIDF_score(IDF:dict,TF:dict)->dict:
    for key, value in TF.items():
        TF[key] = abs(value*IDF[key])
    return TF

def abs_TFIDF_score(IDF:dict,TF:dict):
    for key,value in TF.items():
        if key in IDF.keys():
            TF[key] = abs(value*IDF[key])
        else:
            TF[key] = 0
    return TF

def cosine_score(qry_TFIDF:dict,abs_TFIDF:dict):
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


def cal_average(num:list)->float:
    sum_num = 0
    for t in num:
        sum_num = sum_num + t

    avg = sum_num / len(num)
    return avg



'''
In this method, two IDF are produced, one for each political side's all users.
Take one user from "This side" as development set
For rest of the users as the training set, for both sides, an average score of
the developmen set's 5 best matches is calculated and compared.  
'''

def cross_validate_two_IDF(file_names,that_file_names,this_file,that_file,outputname):
    #For example: if we are examing one of the pro-democratic tweeter uses,
    #"this" refer to all pro-democracy users, that refer to pro_beijing users
    this_len=len(this_file)
    that_len=len(that_file)
    this_avg_cos=[None]*this_len #Every examniee to be examined has 1 place
    that_avg_cos=[None]*this_len
    output = open(outputname, "w",encoding="utf8")


    that_qry_len = len(that_file)
    that_qry_TFIDF = [None] * that_qry_len #saves TFIDF of “that” side
    that_qry_IDF = IDF_score(that_file)

    for i in range(0, that_qry_len):
        that_qry_TFIDF[i] = TF_score(that_file[i])
    # print(qry_TFIDF[0])
    for i in range(0, that_qry_len):
        that_qry_TFIDF[i] = (qry_TFIDF_score(that_qry_IDF, that_qry_TFIDF[i]))
    print("That TFIDF finished")

    for index in range(0,this_len):
        #cross-validation, take one of the persons out and cross-validates him
        output.write(f"{file_names[index][:-26]}\n")

        abs=this_file[index]
        qry=[this_file[x] for x in range(this_len) if x != index]

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
        this_cos_list = [None] * qry_len #Every member from training set has one place
        that_cos_list = [None] * that_len

        for i in range(0, qry_len):
            this_cos_list[i] = cosine_score(qry_TFIDF[i], abs_TFIDF)
            if i>=index:
                j=i+1 #Since we have chosen one development set from the training set, add 1 back in order
                      #to print the correct name
            else:
                j=i
            output.write(f"\t{file_names[index][:-25]}\t{file_names[j][:-25]}\t")
            output.write("Cos_similarity=%.4f\n" % this_cos_list[i])

        for i in range(0,that_len):
            that_cos_list[i] = cosine_score(that_qry_TFIDF[i],abs_TFIDF)
            output.write(f"\t{file_names[index][:-25]}\t{that_file_names[i][:-25]}\t")
            output.write("Cos_similarity=%.4f\n" % that_cos_list[i])

        this_cos_list.sort(reverse=True)
        that_cos_list.sort(reverse=True)
        this_avg_cos[index]=cal_average(this_cos_list[:5])
        that_avg_cos[index]=cal_average(that_cos_list[:5])
        print(index,"done")

        output.write("Average cosine similarity with This=%.4f\t" % this_avg_cos[index])
        output.write("Average cosine similarity with That=%.4f\t" % that_avg_cos[index])
        if this_avg_cos[index] > that_avg_cos[index]:
            output.write("Correct\n\n")
        else :
            output.write("False\n\n")
    output.close()


def cross_validate_one_IDF(file_names,that_file_names,this_file,that_file,outputname):
    #For example: if we are examing one of the pro-democratic tweeter uses,
    #"this" refer to all pro-democracy users, that refer to pro_beijing users
    this_len=len(this_file)
    that_len=len(that_file)
    this_avg_cos=[None]*this_len #Every examniee to be examined has 1 place
    that_avg_cos=[None]*this_len
    output = open(outputname, "w",encoding="utf8")
    Total_correct_num=0

    for index in range(0,this_len):
        #cross-validation, take one person as development set and rest as training set
        output.write(f"{file_names[index][:-25]}\n")

        abs=this_file[index] # abs is the development set
        qry=[this_file[x] for x in range(this_len) if x != index]
        qry_IDF_only=qry+that_file #Corpora IDF is now combination of all person except the development set

        qry_len = len(qry)
        qry_TFIDF = [None] * qry_len
        combined_IDF = IDF_score(qry_IDF_only)

        #calculate the TFIDF score of the development set's opposite side
        that_qry_len = len(that_file)
        that_qry_TFIDF = [None] * that_qry_len

        for i in range(0, that_qry_len):
            that_qry_TFIDF[i] = TF_score(that_file[i])
            # print(qry_TFIDF[0])
        for i in range(0, that_qry_len):
            that_qry_TFIDF[i] = (qry_TFIDF_score(combined_IDF, that_qry_TFIDF[i]))

        for i in range(0, qry_len):
            #calculate the TF score of development set's same side
            qry_TFIDF[i] = TF_score(qry[i])
        for i in range(0, qry_len):
            #calculate the TFIDF score of development set's same side
            qry_TFIDF[i] = (qry_TFIDF_score(combined_IDF, qry_TFIDF[i]))

        abs_TF = TF_score(abs)
        abs_TFIDF = abs_TFIDF_score(combined_IDF, abs_TF)
        this_cos_list = [None] * qry_len #Every examnier has one place
        that_cos_list = [None] * that_len

        cos_dict=dict() #saves TFIDF match score with traning sets
                        # format cos_dict[training_set_name]=[Match Score]
        for i in range(0, qry_len):
            this_cos_list[i] = cosine_score(qry_TFIDF[i], abs_TFIDF)
            if i>=index:
                j=i+1
            else:
                j=i
            cos_dict[file_names[j]]=this_cos_list[i]


        for i in range(0,that_len):
            that_cos_list[i] = cosine_score(that_qry_TFIDF[i],abs_TFIDF)
            cos_dict[that_file_names[i]] = that_cos_list[i]

        cos_dict={k: v for k, v in sorted(cos_dict.items(), key=lambda item: item[1])}
        cos_list=list(cos_dict.items())
        cos_list.reverse()
        #Sort all TFIDF match scores in desending order

        correct_num=0
        wrong_num=0
        for i in cos_list[:5]:
            output.write(f"\t{i[0][:-25]}\t\%.4f\t" % i[1])
            if i[0] in file_names:
                correct_num+=1
                output.write("Correct+1\n")
            elif i[0] in that_file_names:
                wrong_num+=1
                output.write("Wrong+1\n")

        if correct_num > wrong_num:
            output.write("Overall Correct\n\n")
            Total_correct_num+=1
        else:
            output.write("Overall Wrong\n\n")
        print(index,"done")
    output.close()


def main():

    BJ_files = glob.glob('*.BJ')#produces a list of file names
    DM_files = glob.glob('*.DM')
    BJ_filename = "BJ.tweets"
    DM_filename = "DM.tweets"

    merge_files(BJ_files, BJ_filename)#merges tweets from different files in one file
    merge_files(DM_files, DM_filename)

    BJ_ori_file = process_file(BJ_filename)#processes the original merged file for cross-validation usage
    DM_ori_file = process_file(DM_filename)

    cross_validate_one_IDF(BJ_files,DM_files,BJ_ori_file, DM_ori_file,"BJ_new_result.out")
    #cross validate all users from pro-beijing side
    cross_validate_one_IDF(DM_files,BJ_files,DM_ori_file, BJ_ori_file,"DM_new_result.out")
    #cross validate all users from pro-democracy side


main()
