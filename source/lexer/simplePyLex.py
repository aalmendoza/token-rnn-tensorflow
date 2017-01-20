import sys
import os
from lexer.unicodeManager import UnicodeWriter
from lexer.utilities import *
from lexer.fileUtilities import *
from pygments.lexers import get_lexer_for_filename
from pygments import lex
from subprocess import call
import lexer.Android as Android
import re
import lexer.dictUtils as dictUtils
import pickle

METADATAFLAG = True
SKIP_BIG = False
EXPLICIT_TYPE_WRITE = False

#string, string, list of tokens, int, string --> -----
#Given the output directory, the original file type, the tokens to write, and the
#file id, write out the tokens to file
#Precondition: files must be less than MAX_SIZE tokens (large files seem to
#cause problems with Zhaopeng's cache model.
def writeLexedFile(outputFile, lexedWoComments, flag, explicitWrite):
    #print(lexedWoComments)
    assert(len(lexedWoComments) <= MAX_SIZE)
    #Uncomment if you want to copy the actual java file too.
    #Commented out to save space.
    #call(["cp", path, outputDir + "/" + str(i) + "." + fileExtension[2:]])
    # Write to file
    #Output format must be single line and be the input file name + .tokens.
    with open(outputFile, "wb") as f:
        writer = UnicodeWriter(f)
        for t in lexedWoComments:
            token = t[1]
            noWS = token.strip()
            noWS = noWS.replace('\n', '') #Remove new lines
            noWS = noWS.replace(' ', '_') #Replace any remaining internal spaces
            if(noWS == ""):
                continue

            if(flag == "labelled" or flag == "android" or flag == "api"):
                if(explicitWrite == True):
                    noWS = "<" + noWS + "|" + str(t[0]) + ">"
         
            f.write(noWS.encode("utf-8"))
            f.write(' '.encode("utf-8"))
        f.write('\n'.encode("utf-8")) #Without a new line between each file, there can be a problem with the SRILM ngram tools?


def main(sourcePath, outputPath, strFlag, token_split, SKIP_BIG, EXPLICIT_TYPE_WRITE):    
    #Count of Error tokens
    errorCount = 0

    if(token_split.lower() == "api"):
        #Load in internally defined functions
        corpusDefinitions = pickle.load(open(os.path.join(basePath, "definitions.pickle"), 'r'))

    components = sourcePath.split(".")
    fileContents = ""
    with open(sourcePath, 'r') as f:
        fileContents = ''.join(f.readlines())

    lexer = get_lexer_for_filename(sourcePath)
    tokens = lex(fileContents, lexer) # returns a generator of tuples
    tokensList = list(tokens)
    language = languageForLexer(lexer)

    # Strip comments and alter strings
    lexedWoComments = tokensExceptTokenType(tokensList, Token.Comment)
    lexedWoComments = tokensExceptTokenType(lexedWoComments, Token.Literal.String.Doc)
    beforeError = len(lexedWoComments)
    #Remove Things than didn't lex properly
    lexedWoComments = tokensExceptTokenType(lexedWoComments, Token.Error)
    errorCount += beforeError - len(lexedWoComments)

    #if(language == "Javascript"):
    #    lexedWoComments = mergeDollarSign(lexedWoComments)

    lexedWoComments = fixTypes(lexedWoComments, language) #Alter the pygments lexer types to be more comparable between our languages
    lexedWoComments = convertNamespaceTokens(lexedWoComments, language)

    if(token_split.lower() == "full" or token_split.lower() == "labelled" or token_split.lower() == "android" or token_split.lower() == "api"):
        if(strFlag == 0):
            lexedWoComments = modifyStrings(lexedWoComments, underscoreString)
        elif(strFlag == 1):
            lexedWoComments = modifyStrings(lexedWoComments, singleStringToken)
        elif(strFlag == 2):
            lexedWoComments = modifyStrings(lexedWoComments, spaceString)
        elif(strFlag == 3):
            lexedWoComments = modifyStrings(lexedWoComments, singleStringToken)
            #print(lexedWoComments)
            lexedWoComments = collapseStrings(lexedWoComments)
            lexedWoComments = modifyNumbers(lexedWoComments, singleNumberToken)
        else:
            print("Not a valid string handling flag. Valid types are currently 0, 1, 2, and 3")
            quit()

        if(token_split.lower() == "android"):
            lexedWoComments = labelAndroidTypes(lexedWoComments)

    elif(token_split.lower() == "keyword"):            
        lexedWoComments = getKeywords(lexedWoComments, language.lower())
    elif(token_split.lower() == "name"):
        lexedWoComments = getNameTypes(lexedWoComments, language.lower())
    elif(token_split.lower() == "nonname"):
        lexedWoComments = getNonNameTypes(lexedWoComments)
    elif(token_split.lower() == "collapsed"):
        lexedWoComments = modifyStrings(lexedWoComments, singleStringToken)
        lexedWoComments = collapseStrings(lexedWoComments)
        lexedWoComments = modifyNumbers(lexedWoComments, singleNumberToken)
        lexedWoComments = modifyNames(lexedWoComments, singleNameToken)
    else:
        print("Not a valid token split.")
        
    #Remove empty files (all comments).
    if(len(lexedWoComments) == 0):
        print("Skipping: " + sourcePath)
        return

    
    (lineCount, ave, lineDict, lineLengths) = getLineMetrics(lexedWoComments)
    #print(lexedTokens)
    noWSTokens = []
    for t in lexedWoComments:
        noWS = t[1].strip()
        noWS = noWS.replace('\n', '') #Remove new lines
        if(noWS == "" or noWS[0] == Token.Text):
            continue
        noWSTokens.append((t[0],noWS))

    #noWSTokens = lexedWoComments #Experiment on spacing. Didn't seem to matter if newlines were included.

    #print(noWSTokens)
    #print(len(noWSTokens))

    skip = False
    #If over max size, break into chunks of approximately MAX_SIZE at  new lines
    if(not SKIP_BIG and len(noWSTokens) > MAX_SIZE):
        print("Big file: " + sourcePath)
        #print("Lines: " + str(lineCount))
        #print(lineLengths)
        #print(lineDict)
        #SPLIT into chunks of less than MAX_SIZE with each sub file being at least ending in a complete
        #line.
        startIndex = 0
        endIndex = 0
        lastIndex = 0
        
        while(len(noWSTokens[startIndex:]) > MAX_SIZE):
            print("Piece ID: " + str(i))
            #print(lastIndex)
            endIndex = getLastNewLine(noWSTokens, lineDict, startIndex) # What if this is bigger than MAX_SIZE?
            #print("Start: " + str(startIndex))
            #print("End: " + str(endIndex))
            if(endIndex <= startIndex or endIndex+1-startIndex > MAX_SIZE): #Not catching some...
                print("Aberrant File, enormously long line. Discarding.")
                skip = True
                break
                
            #endIndex = getLastNewLine(noWSTokens, startIndex) #This is broken now :(
            print(endIndex)

            print("Printing: " + str(len(noWSTokens[startIndex:endIndex+1])) + " tokens.")
            writeLexedFile(outputPath, noWSTokens[startIndex:endIndex+1], token_split, EXPLICIT_TYPE_WRITE)
            i += 1
            startIndex = endIndex + 1 #Start of the new file one past the end.

        #Write out the last bit
        if(not skip):
            writeLexedFile(outputPath, noWSTokens[startIndex:], token_split, EXPLICIT_TYPE_WRITE)
    elif(len(noWSTokens) <= MAX_SIZE):
        # print("Normal File: " + sourcePath)
        writeLexedFile(outputPath, noWSTokens, token_split, EXPLICIT_TYPE_WRITE)


    #Increment output file count
    if skip:
        skip = False

if __name__ == "__main__":
    if len(sys.argv) < 7:
        print('Usage: python lex.py source_file output_file flag token_split skip_big explicit_type')
        print("Example: python simplePyLex.py ~/CodeNLP/HaskellProjects/ *.hs tests/ 0 full True False")
        print("Flag is 0, 1, 2, or 3 currently")
        print("0 -> replace all spaces in strings with _")
        print("1 -> replace all strings with a <str> tag.")
        print("2 -> add spaces to the ends of the strings")
        print("3 -> collapse strings to <str> and collapses numbers to a type as well.")
        print("token_split is full, keyword, name, labelled, nonname, android, api, or collapsed currently")
        print("labelled keeps all tokens, but attaches labels or name, keyword, or other")
        print("the android option is exclusively for android, and attaches a Android.* to")
        print("All android api references.  Other tokens retain the type from the highlighter.")
        print("Collapsed replaces all the name types (plus Keyword.Type) with their label.")
        print("Collapsed option also forces the string option to 1.")
        print("And finally two y/n options on whether to keep files with over " + str(MAX_SIZE))
        print("tokens and if we want to explicitly have the type <Token|Type> in the output files.")
        quit()
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])