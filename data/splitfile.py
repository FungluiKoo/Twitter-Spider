#! /usr/bin/env python3
# encoding=utf-8

# Usage: python splitfile.py old_file cut_num

import sys

file_name = sys.argv[1]
cut_num = eval(sys.argv[2])
n = len("_2021-01-01_2021-04-15.txt")

fo = list()
for i in range(cut_num):
    out_file_name = file_name[0:-n] + f"{i}" + "_2021-01-01_2021-04-15.txt"
    fo.append(open(file=out_file_name, mode="w", encoding="utf-8"))

with open(file=file_name, mode="r", encoding="utf-8") as fi:
    i = 0
    for line in fi:
        fo[i].write(line)
        i = (i+1) % cut_num

for f in fo:
    f.close()