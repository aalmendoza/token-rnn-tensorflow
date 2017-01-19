#Example input line:
#BrownCorpusca01.txt.out:        <parse>(ROOT (S (NP (DT The) (NNP Fulton) (NNP County) (NNP Grand) (NNP Jury)) (VP (VBD said) (NP-TMP (NNP Friday)) (SBAR (S (NP (NP (DT an) (NN investigation)) (PP (IN of) (NP (NP (NNP Atlanta) (POS 's)) (JJ recent) (JJ primary) (NN election)))) (VP (VBD produced) (`` ``) (NP (DT no) (NN evidence)) ('' '') (SBAR (IN that) (S (NP (DT any) (NNS irregularities)) (VP (VBD took) (NP (NN place))))))))) (. .))) </parse>

#Set of tags used in stanford parser, thanks to:
#https://gist.github.com/nlothian/9240750 + some observations
tag_set = ["ROOT","S", "SBAR", "SBARQ", "SINV", "SQ", "ADJP", "ADVP", "CONJP", "FRAG", "INTJ", "LST", "NAC", "NP", "NX", "PP",
           "PRN", "PRT", "QP", "RRC", "UCP", "VP", "WHADVP","WHADJP", "WHAVP", "WHNP", "WHPP", "X", "CC", "CD", "DT", "EX", 
           "FW", "IN","JJ", "JJR", "JJS", "LS", "MD", "NN", "NNS", "NNP", "NNPS", "PDT", "POS", "PRP", "PRP$", "RB", "RBR", 
           "RBS", "RP", "SYM","TO", "UH", "VB", "VBD", "VBG","VBN", "VBP", "VBZ", "WDT", "WP", "WP$", "WRB","ADV", "NOM","DTV",
           "LGS", "PRD", "PUT","SBJ", "TPC", "VOC","BNF", "DIR","EXT", "LOC","MNR", "PRP", "TMP", "CLR", "SBAR-PRP","CLF", "HLN"
           "TTL","-LRB-", "-RRB-","-NONE","*", "0", "T", "NUL", "NP-TMP"]

punct_set = ["``", "\'\'", ".", ",", ":", "$", "#"]


def getFileName(line):
    return line[:line.find(".")]

def lexParseTree(line): #Simple version
    #Get main section
    tree = line[line.find("<parse>"):]
    #Remove xml on the edges and outer paranthesis? Just XML for now.
    tree = tree.replace("<parse>", "").replace("</parse>", "")
    #Add spaces for each )
    tree = tree.replace("(", " ( ").replace(")", " ) ").replace("\n", " ")
    return tree


#Give a parse tree item one of 4 tags:
#PAREN, TAG, WORD, PUNCT
def tagElement(item, last,stopwords):
    item = item.strip()
    if(item == "(" or item == ")"):
        return "PAREN"
    elif(item in tag_set):
        if(last == "PAREN"):
            return "TAG"
        elif(item in stopwords):
            return "STOPWORD"
        else:
            return "WORD"
    elif(item in punct_set):
        if(last == "PAREN"):
            return "TAG"
        else:
            return "PUNCT"
    else:
        if(item in stopwords):
            return "STOPWORD"
        else:
            return "WORD"

#For a given lexed file, create a csv file with the following:
#Header: token, token_type, token_location
#Note: Token_type will be one of 3 things: PAREN, TAG, WORD
def createMetaDataFile(lexed_tree, metadata_filename,stopwords):
    i = 0
    with open(metadata_filename, 'w') as f:
        f.write("token,token_type,token_location\n")
        tag = "PAREN" #Always starts with a '(' - though we removed it.
        for item in lexed_tree.split():
            tag = tagElement(item, tag,stopwords)
            f.write(",".join(["\"" + item + "\"", tag, str(i), "\n"]))
            i += 1


stopwords = []

with open("stopwords.txt", 'r') as f:
    for line in f:
        stopwords.append(line.lower().strip())

brownFiles = {}

with open('BrownParse.out', 'r') as f:
    for line in f:
        file_name = getFileName(line)
        lexedTree = lexParseTree(line)
        if(file_name in brownFiles):
            brownFiles[file_name] += lexedTree
        else:
            brownFiles[file_name] = lexedTree

#Write out to a token file.
file_id = 0
for file_name, lexed_tree in brownFiles.iteritems():
    with open("../BrownCorpus/LexedConstituencyParse/"+ str(file_id) + ".txt.tokens", 'wb') as f:
        print(file_id)
        metadata_name = "../BrownCorpus/LexedConstituencyParse/" + str(file_id) + ".txt.metadata"
        createMetaDataFile(lexed_tree, metadata_name,stopwords)
        f.write(lexed_tree)
        file_id += 1
