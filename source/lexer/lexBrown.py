import nltk
import sys

punct = [",", ".", "\"", ",\"","'",";", ".\"", "-", "?", "--", ":", "!\"", "?\"", "!", "?--", ".--", "!--", "\'" ,"\'\'", "``", "`", "(", ")", "/"]


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

try:
    outputDir = sys.argv[1]
    noStopwords = int(sys.argv[2])
    if(noStopwords == 1):
        stopwordsFile = sys.argv[3]
except:
    print("usage: python lexBrown.py outputDir filterStopwords [stopwordsFile]")
    print("filterStopwords is 0 or 1, 0 keeps all words, 1 filters the stop words, 2 filters punctuation only")
    print("If 1, supply a file containing the stop words.")
    quit()


stopwords = []

if(noStopwords == 1):
    with open(stopwordsFile, 'r') as f:
        for line in f:
            stopwords.append(line.lower().strip())


i = 0

for fileid in nltk.corpus.brown.fileids():
    words = nltk.corpus.brown.words(fileid)
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
            outputFile.write(w)
            outputFile.write(' ')
        outputFile.write('\n') #Without a new line between each file, there can be a problem with the SRILM ngram tools?
    i += 1