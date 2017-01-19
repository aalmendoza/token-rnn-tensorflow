import sys
import os
from folderManager import Folder

#String, String -> boolean
#Given a file path and import line, tries to determine if the api call is a reference to 
#another module in the project.  This is very basic, just a check if any of the import pieces
#(between the "."s) are a substring of the filepath
def isInternalAPI(filepath, line):
    pieces = line.split(".")
    #if(len(pieces) == 1):
    #    return True
    for p in pieces:
        p = p.lower()
        if(p in filepath and p not in ["java", "f#", "haskell"]):
            return True
    return False

#Input: directory outputfile
#Ouput: 1 file with format:
#File: (Full Path)
#<import statement 1>
#...
#File: (Full Path)
#<import statment 2>

if len(sys.argv) < 2:
    print('Usage: python dumpImports.py input_dir ext output_file')
    print("Example: python dumpImports.py ~/CodeNLP/HaskellProjects/ *.hs haskellImports.txt")
    quit()
   
print(sys.argv)

codeFolder = Folder(os.path.abspath(sys.argv[1]))
# File type to be considered
fileExtension = sys.argv[2]
output_file = sys.argv[3]

internalCount = 0
externalCount = 0
with open(output_file, 'w') as out:
    for path in codeFolder.fullFileNames(fileExtension, recursive=True):
        out.write("File: " + path + "\n")
        try:
            with open(path, 'r') as f:
                for line in f:
                    line = line.replace("\n", "")
                    if(line.strip().startswith("import ") or line.strip().startswith("open ")):
                        shortened = line.replace("import ", "").replace("open ", "")
                        if(isInternalAPI(path, shortened)):
                            internalCount += 1
                            out.write(line + " (Internal)\n")
                        else:
                            externalCount +=1
                            out.write(line + " (External)\n")
        except:
            out.write("Parse Error.")


print("Internal: " + str(internalCount))
print("External: " + str(externalCount))
