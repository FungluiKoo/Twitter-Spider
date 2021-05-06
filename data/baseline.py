#! /usr/bin/env python3
# encoding=utf-8

# Usage: python baseline.py account-beijing.csv account-democracy.csv test-beijing.csv test-democracy.csv

TOP_N = 50
K = 5
OUT_FILE_NAME = "baseline-result.txt"

import sys

file_beijing = sys.argv[1]
file_democracy = sys.argv[2]
test_beijing = sys.argv[3]
test_democracy = sys.argv[4]


def get_distances(a: set, b: set) -> float:
    result = 0
    for word in a:
        if word not in b:
            result += 1
    else:
        result /= TOP_N
    return result


accounts = list()
accounts_beijing = list()
accounts_democracy = list()

with open(file=file_beijing, mode="r", encoding="utf-8") as f:
    for line in f:
        account = line.split("twitter.com/")[-1].strip()
        if len(account)>1:
            accounts.append(account)
            accounts_beijing.append(account)
with open(file=file_democracy, mode="r", encoding="utf-8") as f:
    for line in f:
        account = line.split("twitter.com/")[-1].strip()
        if len(account)>1:
            accounts.append(account)
            accounts_democracy.append(account)

words = dict()
distances = dict()

for account in accounts:
    file_name = account + "_highest.txt"
    s = set()
    with open(file=file_name, mode="r", encoding="utf-8") as fi:
        for row in fi:
            word = row.rstrip()
            if word != "":
                s.add(word)
    words[account] = s
    distances[account] = dict()

for i in range(len(accounts)-1):
    for j in range(i+1,len(accounts)):
        value = get_distances(words[accounts[i]], words[accounts[j]])
        distances[accounts[i]][accounts[j]] = value
        distances[accounts[j]][accounts[i]] = value

with open(file=OUT_FILE_NAME, mode="w", encoding="utf-8") as fo:
    result_cnt = {"True":0, "False":0}
    for account in accounts:
        account_type = "Beijing" if account in accounts_beijing else "Democracy"
        fo.write(f"\n{account}, {account_type}\n")
        itemls=sorted(list(distances[account].items()),key=lambda x:x[1], reverse=False)
        neighbor_beijing_cnt = 0
        for i in range(K):
            neighbor, distance=itemls[i]
            if neighbor in accounts_beijing:
                neighbor_type = "Beijing"
                neighbor_beijing_cnt += 1
            else:
                neighbor_type = "Democracy"
            fo.write(f"\t{neighbor}, {distance}, {neighbor_type}\n")
        else:
            if neighbor_beijing_cnt >= K/2:
                judgement = "True" if account_type=="Beijing" else "False"
                fo.write(f"Predicted as Beijing. {judgement}\n")
                result_cnt[judgement] += 1
            else:
                judgement = "True" if account_type=="Democracy" else "False"
                fo.write(f"Predicted as Democracy. {judgement}\n")
                result_cnt[judgement] += 1
    else:
        fo.write("\nTrue: {}; False: {}\n".format(result_cnt["True"], result_cnt["False"]))
