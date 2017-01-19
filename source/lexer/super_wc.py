import sys
import os
from folderManager import Folder

#This script will produce results similar to wc -w *
#and is usefull when * expands past what the default wc
#can handle

try:
    inputDir = sys.argv[1]
    fileExtension = sys.argv[2]
except:
    print("usage: python super_wc.py inputDir")

codeFolder = Folder(os.path.abspath(inputDir))

sum = 0

for path in codeFolder.fullFileNames(fileExtension, recursive=False):
    count = len(open(path, 'r').read().split())
    sum += count
    print(str(count) + " : " + path)

print("Total: " + str(sum))
