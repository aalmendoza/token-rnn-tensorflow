from .utilities import *
from pygments.lexers import get_lexer_for_filename, get_lexer_by_name, guess_lexer
from pygments import lex
import re
import argparse
import codecs

# Tokenize the code such that line information is kept
# Returns the tokenized code as a string along with the
# corresponding types of each token
def get_tokenization(lexedWoComments):
    tokenized_string = ''
    token_types = []
    curr_line_empty = True
    for t in lexedWoComments:
        token_type = str(t[0])
        token = t[1]
        token_stripped = token.strip()

        if '\n' in token:
            if curr_line_empty:
                if t[0] != Token.Text and token_stripped != '':
                    tokenized_string += token_stripped + "\n"
                    token_types.append(token_type)
            else:
                tokenized_string += token_stripped + "\n"

                # Edge case for stray "/" in code
                if token_stripped == "\\":
                    token_types.append(token_type)
            curr_line_empty = True
        elif t[0] == Token.Text:
            continue
        else:
            curr_line_empty = False
            tokenized_string += token + ' '
            token_types.append(token_type)

    return tokenized_string, token_types

def tokenize_code(code, language, lexer, literal_option):
    tokens = lex(code, lexer)
    tokensList = list(tokens)

    # Strip comments and alter strings
    lexedWoComments = tokensExceptTokenType(tokensList, Token.Comment)
    lexedWoComments = tokensExceptTokenType(lexedWoComments, Token.Literal.String.Doc)
    lexedWoComments = fixTypes(lexedWoComments, language) #Alter the pygments lexer types to be more comparable between our languages
    lexedWoComments = convertNamespaceTokens(lexedWoComments, language)

    if(literal_option == 0):
        lexedWoComments = modifyStrings(lexedWoComments, underscoreString)
    elif(literal_option == 1):
        lexedWoComments = modifyStrings(lexedWoComments, singleStringToken)
    elif(literal_option == 2):
        lexedWoComments = modifyStrings(lexedWoComments, spaceString)
    elif(literal_option == 3):
        lexedWoComments = modifyStrings(lexedWoComments, singleStringToken)
        lexedWoComments = collapseStrings(lexedWoComments)
        lexedWoComments = modifyNumbers(lexedWoComments, singleNumberToken)

    return get_tokenization(lexedWoComments)

# source_file: path of source file to be tokenized
# language: programming language of source file, e.g. "c"
# literal_option:
#   0 -> replace all spaces in strings with _
#   1 -> replace all strings with a <str> tag
#   2 -> add spaces to the ends of the strings
#   3 -> collapse strings to <str> and collapses numbers to a type as well.
def tokenize_file(source_file, language=None, literal_option=3):
    code = ""
    try:
        with codecs.open(source_file, "r",encoding='utf-8', errors='ignore') as f:
            code = f.read()
    except UnicodeDecodeError:
        return '', []

    if language is None:
        try:
            lexer = get_lexer_for_filename(source_file)
        except KeyError: # Not a valid extension
            lexer = guess_lexer(code)
            language = languageForLexer(lexer)
    else:
        lexer = get_lexer_by_name(language)

    return tokenize_code(code, language, lexer, literal_option)