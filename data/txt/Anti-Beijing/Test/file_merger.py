import glob
#This function inputs all .txt files in the directory and writes them in "lines.txt" with \n\n tp
#with \n\n to separete each file

def map_files(file_list):
    for file in file_list:
        with open(file, 'rt',encoding="utf8") as fd:
            yield fd.read()

def merge_files(file_list, filename='first_lines.txt'):
    with open(filename, 'w',encoding="utf8") as f:
        for line in map_files(file_list):
            f.write("%s\n\n" % line)


files = glob.glob("*.txt")
merge_files(files)
