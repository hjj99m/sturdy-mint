# coding: UTF-8
################################################
# Author: Hubert Huang
# Website: http://hubertnote.blogspot.com
################################################
from os import walk
import fnmatch, os.path, configparser
################################################
def my_check_ext(filename, extnames):
    ''' haha '''
    flag = False
    for ext in extnames:
        if fnmatch.fnmatch(filename, ext):
            flag = True
    return flag
################################################
config = configparser.ConfigParser()
config.read('result.txt')

tags = config['CONDITION']['tags'].split(',')
exts = config['CONDITION']['exts'].split(',')
target_dir = config['CONDITION']['target_dir']

################################################
flist = []
fdict = dict()
fn = ''
for (dirpath, dirnames, filenames) in walk(target_dir):
    num = len(filenames)
    for i in range(0, num):
        fn = str(dirpath) + "/" + str(filenames[i])
        if my_check_ext(fn, exts) and os.path.exists(fn):
            try:
                f = open(fn, 'r')
                tmp = list()
                for line in f:
                    for tag in tags:
                        if tag in line and tag not in tmp:
                            tmp.append(tag)
                            fdict[fn] = tmp
            except:
                print('cannot open file:' + fn)
    else:
        pass
################################################
cc = list(fdict.keys())
dd = list(fdict.values())

for w in cc:
    print(w + ':')
    for ww in fdict[w]:
        print(ww)