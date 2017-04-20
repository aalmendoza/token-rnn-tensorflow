'''
Created on Oct 12, 2015

@author: Naji Dmeiri
@author: Bogdan Vasilescu
@author: Casey Casalnuovo
'''
from pygments.token import *
from collections import OrderedDict
import csv
import re

SUPPORTED_LANGUAGE_STRINGS = {
    'Ruby',
    'Python',
    'JavaScript',
    'PHP',
    'Java',
    'Scala',
    'C',
    'C++',
    'Objective-C',
    'Swift',
    'Haskell',
    'Common Lisp',
    'Prolog',
    'FSharp',
    'Clojure'
}


def languageForLexer(lexer):
    """
    :param lexer:   A `Lexer` object as defined in `pygments.lexer`
    :returns:       A string indicating the language supported by the lexer
                    Currently supported return values:  'Ruby',
                                                        'Python',
                                                        'JavaScript',
                                                        'PHP',
                                                        'Java',
                                                        'Scala',
                                                        'C',
                                                        'C++',
                                                        'Objective-C',
                                                        'Swift'
                                                        'Haskell'
                                                        'Common Lisp'
                                                        'Prolog'
                                                        'FSharp'
                                                        'Clojure'
    """
    mapping = {
        'Ruby':         'Ruby',
        'Python':       'Python',
        'JavaScript':   'JavaScript',
        'Php':          'PHP',
        'Java':         'Java',
        'Scala':        'Scala',
        'C':            'C',
        'Cpp':          'C++',
        'Objective-C':  'Objective-C',
        'Swift':        'Swift',
        'Haskell':      'Haskell',
        'Common Lisp':  'Common Lisp',
        'Prolog':       'Prolog',
        'FSharp':       'FSharp',
        'Clojure':      'Clojure'
    }
    #print(lexer.name)
    assert mapping[lexer.name] in SUPPORTED_LANGUAGE_STRINGS # sanity check; can be disabled in release build
    return mapping[lexer.name]


def tokensForTokenType(tokens, tokenType, ignoreSubtypes = False):
    """
    :param tokens:          A list of `Token` objects as defined in `pygments.token`
    :param tokenType:       A `TokenType` object as defined in `pygments.token`
    :param ignoreSubtypes:  When set to True, the returned list will include subtypes of `tokenType` ; default is `False`.
    :returns:               An iterable of tuples that each hold information about a `tokenType` tokens.
    """
    if tokenType not in STANDARD_TYPES:
        raise ValueError("%s is not a standard Pygments token type." % tokenType)

    if not ignoreSubtypes:
        return [t for t in tokens if is_token_subtype(t[0], tokenType)]
    else:
        return [t for t in tokens if t[0] == tokenType]

def isSubTypeIn(token, tokenTypes):
    for t in tokenTypes:
        if(is_token_subtype(token[0], t)):
            return True

    return False

def tokensForTokenTypes(tokens, tokenTypes, ignoreSubtypes = False):
    """
    :param tokens:          A list of `Token` objects as defined in `pygments.token`
    :param tokenTypes:       A list of `TokenType` object as defined in `pygments.token`
    :param ignoreSubtypes:  When set to True, the returned list will include subtypes of `tokenType` ; default is `False`.
    :returns:               An iterable of tuples that each hold information about a `tokenType` tokens.
    """
    for t in tokenTypes: 
        if(t not in STANDARD_TYPES):  
            raise ValueError("%s is not a standard Pygments token type." % tokenType)

    if not ignoreSubtypes:
        return [t for t in tokens if isSubTypeIn(t, tokenTypes)]
    else:
        return [t for t in tokens if t[0] in tokenTypes]


def tokensExceptTokenType(tokens, tokenType, ignoreSubtypes = False, retainedTypes = []):
    """
    :param tokens:          A list of `Token` objects as defined in `pygments.token`
    :param tokenType:       A `TokenType` object as defined in `pygments.token`
    :param ignoreSubtypes:  When set to True, the returned list will include subtypes of `tokenType` ; default is `False`.
    :param retainedTypes:   Specific subtypes of the excluded type we wish to keep.  (Applies when ignoreSubtypes = False)
    :returns:               An iterable of tuples that each hold information about a `tokenType` tokens.
    """
    if tokenType not in STANDARD_TYPES:
        raise ValueError("%s is not a standard Pygments token type." % tokenType)

    if not ignoreSubtypes:
        return [t for t in tokens if (not is_token_subtype(t[0], tokenType)) or (t[0] in retainedTypes)]
    else:
        return [t for t in tokens if not t[0] == tokenType]

#min.js files have newlines removed.  We need them to split big files
#def preprocessJSMinFile(filename):
#    return jsbeautifier.beautify_file(filename)


#Return a list of tokens of the keywords/reserved words for a
#language.  The Pygments token reprsentation may may vary depending
# on the language, so you'll need to implement a new one for each 
#language you want to support.
#Currently supports: Java, Haskell
def getKeywords(tokens, language):
    if(language.lower() == "java"):
        tokens = tokensForTokenType(tokens, Token.Keyword)
        tokens = tokensExceptTokenType(tokens, Token.Keyword.Type)
    elif(language.lower() == "haskell"):
        #Apparently 'error' is not a haskell keyword
        tokens = tokensForTokenType(tokens, Token.Keyword) + tokensForTokenType(tokens, Token.Operator.Word) # + tokensForTokenType(tokens, Token.Name.Exception)
        tokens = tokensExceptTokenType(tokens, Token.Keyword.Type)
    else:
        print("That language type is not supported for keyword extraction.")
        quit()

    return tokens

#Return a list of tokens of the types (variable, class, functions) for a
#language.  The Pygments token reprsentation may may vary depending
# on the language, so you'll need to implement a new one for each 
#language you want to support.
#Currently supports: Java, Haskell
def getNameTypes(tokens, language):
    if(language.lower() == "java"):
        tokens = tokensForTokenTypes(tokens, [Token.Name, Token.Keyword.Type])
        tokens = tokensExceptTokenType(tokens, Token.Name.Builtin)
        #tokens = tokensExceptTokenType(tokens, Token.Name.Namespace)
    elif(language.lower() == "haskell"):
        tokens = tokensForTokenTypes(tokens, [Token.Name, Token.Keyword.Type])
        tokens = tokensExceptTokenType(tokens, Token.Name.Builtin)
    elif(language.lower() == "fsharp"):
        tokens = tokensForTokenTypes(tokens, [Token.Name, Token.Keyword.Type])
        tokens = tokensExceptTokenType(tokens, Token.Name.Builtin)
        #tokens = tokensExceptTokenType(tokens, Token.Name.Namespace)
    elif(language.lower() == "ruby"):
        tokens = tokensForTokenTypes(tokens, [Token.Name, Token.Keyword.Type]) #No builtins?
        tokens = tokensExceptTokenType(tokens, Token.Name.Builtin)
    elif(language.lower() == "clojure"):
        tokens = tokensForTokenTypes(tokens, [Token.Name, Token.Keyword.Type]) #Builtins removed earlier
        tokens = tokensExceptTokenType(tokens, Token.Name.Builtin)
    elif(language.lower() == "c"):
        tokens = tokensForTokenTypes(tokens, [Token.Name, Token.Keyword.Type]) #Builtins removed earlier
        tokens = tokensExceptTokenType(tokens, Token.Name.Builtin)
    else:
        print("That language type is not supported for name extraction.")
        quit()

    return tokens

#Return a list of token types with name types (except for builtins) excluded.  Complement of getNameTypes
#TODO: More language logic necessary if getNameTypes winds up with different language behavior.
def getNonNameTypes(tokens):
    tokens = tokensExceptTokenType(tokens, Token.Name, False, [Token.Name.Builtin])
    return tokens

#Given a list of tokens and a function of the form string token -> string token
#Modify all tokens of String.Literal type according to the function
def modifyStrings(tokens, modifyFunc):
    return [modifyFunc(t) if is_token_subtype(t[0], Token.Literal.String) else t for t in tokens]

#Modify all tokens of the Number type according to the function
def modifyNumbers(tokens, modifyFunc):
    return [modifyFunc(t) if is_token_subtype(t[0], Token.Number) else t for t in tokens]

def modifyNames(tokens, modifyFunc):
    return [modifyFunc(t) if (is_token_subtype(t[0], Token.Name) or t[0] == Token.Keyword.Type) else t for t in tokens]

#Replace spaces in the token with underscores
def underscoreString(strToken):
    return (strToken[0], strToken[1].replace(" ", "_"))

#Replace all strings with a <str> token
def singleStringToken(strToken):
    return (strToken[0], "<str>")

#Handles the case where there are baskslahes in the string to reduce to a single item.
def collapseStrings(tokens):
    if len(tokens) == 0:
        return []

    newTokens = []
    newTokens.append(tokens[0])
    for t in tokens[1:]:
        if(not is_token_subtype(t[0], Token.Literal.String)):
            #if(is_token_subtype(curToken[0], Token.String)):
            #    newTokens.append(curToken)
            newTokens.append(t)
        elif (is_token_subtype(t[0], Token.Literal.String) and (not is_token_subtype(newTokens[-1][0], Token.Literal.String))): #skip String repeats
            newTokens.append(t)


    return newTokens
     
        

#Ensure that all string tokens have spaces after the initial " and before the
#closing "
def spaceString(strToken):
    assert(strToken[1][0] == "\"")
    assert(strToken[1][len(strToken[1]) - 1] == "\"")
    return (strToken[0], strToken[1][:1] + " " + strToken[1][1:len(strToken[1])-1] + " " + strToken[1][len(strToken[1])-1])

#Currently can handle Hex, Float, Integer, Oct, Bin types, if something else, return <num>
def singleNumberToken(numToken):
    if(numToken[0] == Token.Literal.Number.Integer):
        return(numToken[0], "<int>")
    elif(numToken[0] == Token.Literal.Number.Float):
        return(numToken[0], "<float>")
    elif(numToken[0] == Token.Literal.Number.Oct):
        return(numToken[0], "<oct>")
    elif(numToken[0] == Token.Literal.Number.Bin):
        return(numToken[0], "<bin>")
    elif(numToken[0] == Token.Literal.Number.Hex):
        return(numToken[0], "<hex>")
    else:
        return(numToken[0], "<num>")

def singleNameToken(nameToken):
    if(nameToken[0] == Token.Name):
        return(nameToken[0], "<name>")
    elif(nameToken[0] == Token.Name.Class):
        return(nameToken[0], "<class>")
    elif(nameToken[0] == Token.Name.Namespace):
        return(nameToken[0], "<namespace>")
    elif(nameToken[0] == Token.Name.Function):
        return(nameToken[0], "<function>")
    elif(nameToken[0] == Token.Name.Attribute):
        return(nameToken[0], "<attribute>")
    elif(nameToken[0] == Token.Name.Label):
        return(nameToken[0], "<label>")
    elif(nameToken[0] == Token.Keyword.Type):
        return(nameToken[0], "<type>")
    elif(nameToken[0] == Token.Name.Variable):
        return(nameToken[0], "<variable>")
    elif(nameToken[0] == Token.Name.Decorator or nameToken[0] == Token.Name.Builtin or Token.Name.Exception[0]):
        return nameToken
    else: #Not a name?
        print("Name Conversion - Unrecognized Type:")
        print(nameToken)
        return nameToken

def convertNamespaceToken(text, tokenType):
    #assert(tokenType == "Token.Name.Namespace" or tokenType == "Android.Namespace")
    pieces = text.split(" ")
    next = ""
    for p in pieces:
        if(p == "."):
            next += "<.|Token.Punctuation> "
        else:
            next += "<" + p + "|" + tokenType + "> "
    return next.strip()

def convertNamespaceTokens(tokens, language):
    newTokens = []
    for t in tokens:
        if(t[0] == Token.Name.Namespace):
            pieces = t[1].split(".")
            i = 0
            for p in pieces:
                newTokens.append((t[0], p))
                if(i < len(pieces) -1):
                    newTokens.append((Token.Punctuation, "."))
                i += 1
        else:
            newTokens.append(t)
  
    return newTokens

#In general, some of the values returned by the pygments lexer don't
#compare well with other languages or fit into the categories we
#want.  This general function to fix all the issues observed in the data.
def fixTypes(tokens, language):
    newTokens = []
    i = 0
    if(language == "Java"):
        #In java we:
        #1)Remap the boolean and null? keywords to be literals. (done in mergeEntropy as these and only these are Token.Keyword.Constant
        #2)What about Decorators?  I think this is okay b/c these are mapped to single unique type like the boolean literals are.
        return tokens
    elif(language == "Haskell"):
        #1) Anonymous functions have name "\" and the next sequence of word characters are the ARGUMENTS to it
        #Prem recommends treating this as an operator.
        #2) Remap true and false with Token.Keyword.Type to Token.Keyword.Constant (then it will be remapped with Java's later).
        #3) Fix keywords (often from the haskell language extensions) forall, foreign, family, mdo, proc, and rec
        #This will change if they are Token.Name and Not Token.Name.Function.  rec is skipped b/c it was observed to often be just a
        #a normal name
        #family must come after data or type keyword
        #foreign + proc seem to be the only ones in the base set.
        #4) Relabel the Keyword.Types that are purely non word characters.
        while i < len(tokens):
            #print(i)
            if(tokens[i][0] == Token.Keyword.Type and tokens[i][1].strip() in ("True", "False")):
                newTokens.append((Token.Keyword.Constant, tokens[i][1]))
            elif(tokens[i][0] == Token.Name.Function and tokens[i][1].strip() == "\\"): 
                newTokens.append((Token.Operator, tokens[i][1]))
            elif(tokens[i][0] == Token.Keyword.Type and re.match("^[\W]+$", tokens[i][1].strip()) != None): #[], :, :+ :~: observed
                newTokens.append((Token.Name.Builtin, tokens[i][1]))
            elif(tokens[i][0] == Token.Name and (tokens[i][1].strip() in ("proc", "forall", "mdo"))):
                newTokens.append((Token.Keyword, tokens[i][1]))
            elif(tokens[i][0] == Token.Name.Function and tokens[i][1].strip() == "foreign"):
                newTokens.append((Token.Keyword, tokens[i][1]))
            elif(tokens[i][1].strip() == "family" and i >= 2):
                #print(tokens[i-5:i+5])
                if(tokens[i-2][1].strip() == "data" or tokens[i-2][1].strip() == "type"):
                    newTokens.append((Token.Keyword, tokens[i][1]))
                else:
                    newTokens.append(tokens[i])
            elif(tokens[i][1].strip() == "null" and tokens[i][0] == Token.Name):
                newTokens.append((Token.Keyword.Constant, tokens[i][1]))
            else:
                newTokens.append(tokens[i])

            i += 1
        return newTokens
    elif(language == "Ruby"):
        #1) Remap true and false with Token.Keyword.Pseudo to Token.Keyword.Constant
        #2) Remap the following to Token.Keyword:
        #__ENCODING__ is Token.Name
        #__END__ is Token.Name.Constant
        #__FILE__ is Token.Name.Builtin.Psuedo
        #__LINE__ is Token.Name.Builtin.Psuedo
        #Remap Token.Name.Builtin to Token.Name
        #Move true, false, nil to Token.Keyword.Constant (Keyword/Literal)
        while i < len(tokens):
            if(tokens[i][1].strip() == "__ENCODING__" or tokens[i][1].strip() == "__END__" or tokens[i][1].strip() == "__FILE__" or tokens[i][1].strip() == "__LINE__"):
                newTokens.append((Token.Keyword, tokens[i][1]))
            elif(tokens[i][0] == Token.Name.Builtin):
                newTokens.append((Token.Name, tokens[i][1]))
            elif(tokens[i][0] == Token.Keyword.Pseudo and tokens[i][1].strip() in ("nil", "true", "false")):
                newTokens.append((Token.Keyword.Constant, tokens[i][1]))
            else:
                newTokens.append(tokens[i])
            i += 1
        return newTokens        
    elif(language == "Clojure"):
        #1)Split / and . in Variables
        #2)Fix booleans and nil to Token.Keyword.Constant
        #3)Split Token.Name.Builtin into operators and Names.
        #4)=> Is a Midje (test suite) operator, --> and ->> are clojure macros. Is calling them operators is more fair?
        #Also % or %1, %2, etc are placeholders for anonymous functions.  Keep them as Names too?
        #5)Add in the rest of the special forms.  Avoid Token.Name.Variable designations as they are not the special forms.
        while i < len(tokens):
            if(tokens[i][0] == Token.Name.Variable and tokens[i][1].strip() in ("nil", "true", "false")):
                newTokens.append((Token.Keyword.Constant, tokens[i][1]))
            elif(tokens[i][0] == Token.Name.Builtin):
                if(tokens[i][1].strip() in ("*", "+", "-", "->", "..", "/", "<", "<=", "=","==", ">", ">=")):
                    newTokens.append((Token.Operator, tokens[i][1]))
                else:
                    newTokens.append((Token.Name, tokens[i][1]))
            elif(tokens[i][0] == Token.Name.Function and tokens[i][1].strip() in ("recur", "set!", "moniter-enter", "moniter-exit", "throw", "try", "catch", "finally")):
                newTokens.append((Token.Keyword, tokens[i][1]))
            elif(is_token_subtype(tokens[i][0], Token.Name) and "/" in tokens[i][1]):
                #print("SPLIT ME!")
                pieces = tokens[i][1].split("/")
                newTokens.append((tokens[i][0], pieces[0]))
                for p in pieces[1:]:
                    newTokens.append((Token.Punctuation, "/"))
                    newTokens.append((tokens[i][0], p))
            elif(is_token_subtype(tokens[i][0], Token.Name) and "." in tokens[i][1][1:-1]): #contains a dot inside, not at edges
                pieces = tokens[i][1].split(".")
                newTokens.append((tokens[i][0], pieces[0]))
                for p in pieces[1:]:
                    newTokens.append((Token.Punctuation, "."))
                    newTokens.append((tokens[i][0], p))
            elif(is_token_subtype(tokens[i][0], Token.Name) and tokens[i][1].strip() in ("=>", "->>", "-->")):
                newTokens.append((Token.Operator, tokens[i][1]))
            else:
                newTokens.append(tokens[i])

            i += 1
        return newTokens
    elif(language == "C"):
        while i < len(tokens):
            #Remap Name.Builtin to Literals
            if(tokens[i][0] == Token.Name.Builtin):
                newTokens.append((Token.Literal, tokens[i][1]))
            else:
                newTokens.append(tokens[i])

            i += 1
        return newTokens
        
    else: #No remapping for other languages yet
        print("No type remap for this language implemented")
        return tokens  

#If we've merge a token and its type like <"Token"|Type>, return "Token"
def removeLabel(tokenString):
    if("|Token." in tokenString):
        tokenString = tokenString[1:-1]
        return tokenString[:tokenString.rfind("|Token")]
    else: #Ignore unlabeled tokens
        return tokenString            
