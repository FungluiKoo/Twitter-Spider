#! /usr/bin/env python3
# encoding=utf-8

# Usage: python count-freq.py accounts.csv

TOP_N = 50

import sys

account_list = sys.argv[1]

accounts = list()

with open(file=account_list, mode="r", encoding="utf-8") as f:
    for line in f:
        account = line.split("twitter.com/")[-1].strip()
        if len(account)>1:
            accounts.append(account)


for account in accounts:
    file_name = account + "_2021-01-01_2021-04-15"
    count = dict()
    with open(file=file_name+".txt", mode="r", encoding="utf-8") as fi:
        for row in fi:
            words = row.rstrip().lower().split(",")
            for word in words:
                count[word] = count.get(word, 0) + 1
    with open(file=account+"_highest.txt", mode="w", encoding="utf-8") as fo:
        itemls=sorted(list(count.items()),key=lambda x:x[1], reverse=True)
        for i in range(TOP_N):
            word, count=itemls[i]
            fo.write(f"{word}\n")