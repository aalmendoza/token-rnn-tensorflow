import os
from lexer.utilities import *
from pygments.lexers import get_lexer_for_filename
from pygments import lex

MAX_SIZE = 10000

def getLastNewLine(lexedTokens, lineDict, fileStart):
    index = fileStart + MAX_SIZE-1
    if(index >= len(lineDict)):
        return len(lineDict) -1

    curLine = lineDict[index]
    for nC in reversed(range(index)):
        if(lineDict[nC] < curLine):
            return nC

    return len(lineDict) - 1
        
#Get the last newline in the list before fileStart + MAX_SIZE
#def getLastNewLine(lexedWoComments, fileStart):
#    index = fileStart+MAX_SIZE-1
#    for t in reversed(lexedWoComments[fileStart:fileStart+MAX_SIZE]):
#        if(t[0] == Token.Text and t[1] == u'\n'):  #Find closest new line to where we want to break
#            return index
#
#        index -= 1
#
#    return fileStart+MAX_SIZE-1 #We've reached the end of the big file.

def getLineMetrics(lexedTokens):
    lineCount = 1
    averageLineLength = 0.0
    currentLength = 0
    lineDict = {} #Map the index of the token in the line.
    lineLengths = {}
    i = 0
    for token in lexedTokens:
        if (token[1].strip() != ""):
            currentLength += 1
            lineDict[i] = lineCount
            i += 1

        if("\n" in token[1] or "\r\n" in token[1]):
            lineLengths[lineCount] = currentLength
            lineCount += 1
            averageLineLength += currentLength
            currentLength = 0



        #print(token)
        #print(lineCount)
        #print(averageLineLength)
        #print(currentLength)
    lineLengths[lineCount] = currentLength # Fix last line.
        
    if(lineCount != 0):
        return (lineCount, averageLineLength/lineCount, lineDict, lineLengths)
    else:
        return (0, 0, {})

def getProjectAndFilename(filePath, basePath):
    if(not basePath.endswith("/")):
        basePath = basePath + "/"
    project = filePath.replace(basePath, "").split("/")[0]
    file_name = filePath.replace(basePath + project, "")
    return (project, file_name)
