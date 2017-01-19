import os
import sys
import nltk
import codecs
import re
from folderManager import Folder

MAX_FILE_SIZE = 10000

#TODO, this isn't really handling contractions well...
def filterStopwords(toRemove, text):
    #Also include punctuation
    punct = [",", ".", "\"", ",\"","'",";", ".\"", "-", "?", "--", ":", "!\"", "?\"", "!", "?--", ".--", "!--", "\'" ,"\'\'", "``", "`", "(", ")", "%", "||", "|", "$", "&", "#", "=", "/", "*"]
    nonWord = "[\W]+"
    word = "[a-zA-Z0-9_\n]+"
    temp = []
    for t in filter(lambda t: t.lower() not in toRemove, text):
        tmp = t
        if(tmp not in toRemove):
            if(re.match(word, tmp) != None): #Toss out sequences without any alpha numeric characters.
                for p in punct:
                    tmp = tmp.replace(p, "")

                temp.append(tmp)

    return temp

#There is quite a bit of mark up in the wikipedia corpus.  Can I clean it up efficiently?
#Examples from our sample:
#s
def removeWikiMarkup(text):
    return

#Divid file into ~10000 word files, cutting off at the last sentence (".") before 10000 tokens
def divideBigFile(bigFileTokens):
    print("Spliting file of size: " + str(len(bigFileTokens)))
    assert(len(bigFileTokens) > MAX_FILE_SIZE)
    start = 0
    pieces = []
    while(start < len(bigFileTokens)):
        end_found = False
        next_piece = bigFileTokens[start:start+MAX_FILE_SIZE]
        end = start+MAX_FILE_SIZE
        if(len(next_piece) < MAX_FILE_SIZE): #Last piece
            pieces.append(next_piece)
            break
        else:
            for token in reversed(next_piece):
                if(token == ".\n"):
                    pieces.append(next_piece[start:end])
                    start = end
                    end_found = True
                    break
                end -= 1
            assert(end_found) #Files shouldn't have 10000 + word sentences.

    return pieces
        
#string, int, string, int, list-->
#Given the English text of a wikipedia entry, use nltk to lex it and write
#it out to directory/<outputFileNum>.txt.tokens
def lexWikiFile(text, outputFileNum, directory, noStopwords, stopwords):
    print(outputFileNum)
    raw_tokens = nltk.word_tokenize(" ".join(text))
    tokens = []
    for t in raw_tokens: #Put one sentence on each line.
        if(t == "."):
            if(noStopwords == 1):
                tokens.append("\n")
            else:
                tokens.append(".\n")
        else:
            tokens.append(t)

    if(noStopwords == 1):
        tokens = filterStopwords(stopwords, tokens)
    

    if(len(tokens) > MAX_FILE_SIZE):
        try:
            pieces = divideBigFile(tokens)
            for t in pieces:
                with codecs.open(directory + "/" + str(outputFileNum) + ".txt.tokens",'w',encoding='utf8') as f:
                    f.write(" ".join(t))
                outputFileNum += 1
        except:
            print("File line error.")
    else:
        with codecs.open(directory + "/" + str(outputFileNum) + ".txt.tokens",'w',encoding='utf8') as f:
            f.write(" ".join(tokens))
        outputFileNum += 1

    return outputFileNum

try:
    inputDir = sys.argv[1]
    outputDir = sys.argv[2]
    noStopwords = int(sys.argv[3])
    if(noStopwords == 1):
        stopwordsFile = sys.argv[4]
except:
    print("usage: python wikiCorpusLexer.py inputDir outputDir filterStopwords [stopwordsFiles]")
    print("Subset is 0 or 1, 0 keeps all words, 1 filters the stop words.")
    print("If 1, supply a file containing the stop words.")
    quit()

stopwords = []

if(noStopwords == 1):
    with open(stopwordsFile, 'r') as f:
        for line in f:
            stopwords.append(line.lower().strip())

basePath = os.path.abspath(inputDir)
corpusFolder = Folder(basePath)

inArticle = False
articleText = []
i = 0

for path in corpusFolder.fullFileNames("*.txt", recursive=False):
#Read in inputFile
    with codecs.open(path,'r',encoding='latin1', errors='ignore') as f: #Wikipedia English is UTF-08, so there shouldn't be errors?
        for line in f:
            if(line.startswith("<doc")): #Some metadata here that might be useful
                inArticle = True
            elif(line.startswith("</doc")):
                inArticle = False
                i = lexWikiFile(articleText, i, outputDir, noStopwords, stopwords)
                articleText = []
            elif(inArticle and line.strip() != "ENDOFARTICLE."):
                articleText.append(line)

for path in corpusFolder.fullFileNames("*.txt.tokens", recursive=False):
#Read in inputFile
    with codecs.open(path,'r',encoding='latin1', errors='ignore') as f: #Wikipedia English is UTF-08, so there shouldn't be errors?
        articleText = f.readlines()
        i = i = lexWikiFile(articleText, i, outputDir, noStopwords, stopwords)
        
