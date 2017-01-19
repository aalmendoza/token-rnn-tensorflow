#This file does a "first pass" so that we can get the set of 
#internally designed functions for a set of projects and relabel
#them in the lexer.

import sys
import os
from folderManager import Folder
from unicodeManager import UnicodeWriter
from utilities import *
from fileUtilities import *
from pygments.lexers import get_lexer_for_filename
from pygments import lex
import dictUtils
import pickle

try:
    # Path to root folder containing the source code
    basePath = os.path.abspath(sys.argv[1])
    codeFolder = Folder(basePath)

    #print(codeFolder)

    # File type to be considered
    fileExtension = sys.argv[2]
except:
    print("usage: python apiFinder.py input_dir file_ext")
    print("e.g. python apiFinder.py ~/CodeNLP/HaskellProjects/ *.hs")
    quit()

#Project -> File (Or Class?) -> functionName 
corpusDefinitions = {}


for path in codeFolder.fullFileNames(fileExtension, recursive=False):
    #print("In Loop!")
    if(True):
    #try:
        fileContents = ''.join(open(path, 'r').readlines())
        lexer = get_lexer_for_filename(path)
        tokens = lex(fileContents, lexer) # returns a generator of tuples
        tokensList = list(tokens)
        language = languageForLexer(lexer)
        # Strip comments
        lexedWoComments = tokensExceptTokenType(tokensList, Token.Comment)
        lexedWoComments = tokensExceptTokenType(lexedWoComments, Token.Literal.String.Doc)
        lexedWoComments = tokensExceptTokenType(lexedWoComments, Token.Text)
        (project, file_name) = getProjectAndFilename(path, basePath)
        print("File: " + path)
        #corpusDefinitions[project][file_name] = getFunctionDefinitions(lexedWoComments, language)
        corpusDefinitions = dictUtils.addToDictSet(corpusDefinitions, project, getFunctionDefinitions(lexedWoComments, language))
        #getFunctionDefinitions(lexedWoComments, language)
    #except:
    #    print("Failed: " + path)


pickle.dump(corpusDefinitions, open(os.path.join(basePath, "definitions.pickle"), 'w'))
    
    
