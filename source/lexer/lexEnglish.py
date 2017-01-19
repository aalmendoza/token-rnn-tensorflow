import nltk
import sys
import re

punct = [",", ".", "\"", ",\"","'",";", ".\"", "-", "?", "--", ":", "!\"", "?\"", "!", "?--", ".--", "!--", "\'" ,"\'\'", "``", "`", "(", ")", "/"]


#Is the line all capital letter except for punctuation.
def isTitle(line):
    return re.search("^[ A-Z\W]+$",line.strip()) != None



def removePunct(text):
    newText = []
    for t in text:
        tmp = t
        if(tmp not in punct):
            for p in punct:
                tmp = tmp.replace(p, "")
            
            newText.append(tmp)

    return newText

#TODO, this isn't really handling contractions well...
def filterStopwords(toRemove, text):
    #Also include punctuation

    temp = []
    for t in filter(lambda t: t.lower() not in toRemove, text):
        tmp = t
        if(tmp not in toRemove):
            for p in punct:
                tmp = tmp.replace(p, "")
            temp.append(tmp)

    return temp

def processFile(words, fileid, outputDir, noStopwords):    
    if(noStopwords == 1):
        words = filterStopwords(stopwords, words)
    elif(noStopwords == 2):
        words = removePunct(words)

    with open(outputDir + "/" + str(i) + ".tokens", "w") as outputFile:
        for w in words:
            #print(w)
            w = w.strip().replace('\n', '')
            if(w == ""):
                continue
            outputFile.write(w.encode('utf8'))
            outputFile.write(' ')
        outputFile.write('\n') #Without a new line between each file, there can be a problem with the SRILM ngram tools?


try:
    inputDir = sys.argv[1]
    fileType = sys.argv[2]
    outputDir = sys.argv[3]
    noStopwords = int(sys.argv[4])
    if(noStopwords == 1):
        stopwordsFile = sys.argv[5]
except:
    print("usage: python lexEnglish.py inputDir fileType outputDir filterStopwords [stopwordsFile]")
    print("filterStopwords is 0 or 1, 0 keeps all words, 1 filters the stop words, 2 filters punctuation only")
    print("If 1, supply a file containing the stop words.")
    quit()


stopwords = []

if(noStopwords == 1):
    with open(stopwordsFile, 'r') as f:
        for line in f:
            stopwords.append(line.lower().strip())

i = 0
words = []
first = True

if(".txt" in inputDir): #Check if single file
    with open(inputDir, 'r') as f:
        for line in f:
            if(first== True):
                first = False
            elif(isTitle(line)):
                processFile(words, i, outputDir, noStopwords)
                words = []
                i += 1
            else:
                words += line.split(" ")

else:
    corpus = nltk.corpus.PlaintextCorpusReader(inputDir, fileType) 
    #,word_tokenizer=nltk.tokenize.regexp.WhitespaceTokenizer())

    for fileid in corpus.fileids():
        words = corpus.words(inputDir + "/" + fileid)
        processFile(words, fileid, outputDir, noStopwords)
        i += 1
