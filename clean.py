#! /usr/bin/env python3
# encoding=utf-8

# Usage: python clean.py [file_name.csv]

import csv
import jieba
import opencc
import re
import sys

in_file = sys.argv[1]
converter = opencc.OpenCC('t2s.json')
jieba.load_userdict("../dict.txt")

def clean(txt: str) -> str:
    # Remove "Quote Tweet" patterns
    txt = re.sub(\
        r"Quote Tweet.+@[A-z0-9_]{1,15}(.+(government.+|政府.+|state-affiliated media|官方媒体))?\s*.\s*(Jan|Feb|Mar|Apr)\s[1-3]?[0-9]",\
        "", txt, flags=re.DOTALL|re.MULTILINE)
    # Remove "Replying to" patterns
    txt = re.sub(\
        r"Replying to\s+((@[A-z0-9_]{1,15}\s+)+and\s+)?@[A-z0-9_]{1,15}",\
        "", txt)
    # Remove other Twitter IDs (rules: https://help.twitter.com/en/managing-your-account/twitter-username-rules)
    txt = re.sub(r"@[A-z0-9_]{1,15}\.?", "", txt)
    # Remove URLs
    txt = re.sub(\
        r"(https?://)?([-A-z0-9_]+\.)+[A-z]{2,4}(/[-A-z0-9~!@#%&_+=:\.\?]+)*/?…?",\
        "", txt)
    # Remove views
    txt = re.sub(r"[0-9,\.]*[0-9](K|M)?\sviews", "", txt)
    return converter.convert(txt)

fo = open(file=in_file[:-3]+"txt", mode="w", encoding="utf-8")

with open(file=in_file, mode="r", encoding="utf-8", newline='') as fi:
    csvreader = csv.reader(fi)
    next(csvreader) # ignores header
    for row in csvreader:
        txt = clean(row[1])
        ls = [x for x in jieba.cut(txt) if x.isalpha() or ("64" in x) or ("89" in x)]
        fo.write(",".join(ls)+"\n")

fo.close()