from lexer.utilities import *
from pygments.lexers import get_lexer_for_filename, get_lexer_by_name, guess_lexer
from pygments import lex
import re
import argparse

# Keep Lines?
def get_tokenization(lexedWoComments):
    res = ''
    curr_line_empty = True
    for t in lexedWoComments:
        token = t[1]
        token_stripped = token.strip()

        if '\n' in token:
            if curr_line_empty:
                if t[0] != Token.Text and token_stripped != '':
                    res += token_stripped + "\n"
            else:
                res += token_stripped + "\n"
            curr_line_empty = True
        elif t[0] == Token.Text:
            continue
        else:
            curr_line_empty = False
            res += token + ' '

    return res

def tokenize_code(code, literal_handle=3, language=None):
    if language is None:
        lexer = guess_lexer(code)
    else:
        lexer = get_lexer_by_name(language)

    tokens = lex(code, lexer)
    tokensList = list(tokens)

    # Strip comments and alter strings
    lexedWoComments = tokensExceptTokenType(tokensList, Token.Comment)
    lexedWoComments = tokensExceptTokenType(lexedWoComments, Token.Literal.String.Doc)
    lexedWoComments = fixTypes(lexedWoComments, language) #Alter the pygments lexer types to be more comparable between our languages
    lexedWoComments = convertNamespaceTokens(lexedWoComments, language)

    if(literal_handle == 0):
        lexedWoComments = modifyStrings(lexedWoComments, underscoreString)
    elif(literal_handle == 1):
        lexedWoComments = modifyStrings(lexedWoComments, singleStringToken)
    elif(literal_handle == 2):
        lexedWoComments = modifyStrings(lexedWoComments, spaceString)
    elif(literal_handle == 3):
        lexedWoComments = modifyStrings(lexedWoComments, singleStringToken)
        lexedWoComments = collapseStrings(lexedWoComments)
        lexedWoComments = modifyNumbers(lexedWoComments, singleNumberToken)

    return get_tokenization(lexedWoComments)


def tokenize_file(source_file, literal_handle):
    code = ""
    with open(source_file, 'r') as f:
        code = ''.join(f.readlines())

    language = languageForLexer(lexer)
    return tokenize_code(code, literal_handle, language)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--source_file', type=str,
                       help='source file to be tokenized')
    parser.add_argument('--literal_handle', type=int, default=3,
                       help="0 -> replace all spaces in strings with _\n"
                            "1 -> replace all strings with a <str> tag\n"
                            "2 -> add spaces to the ends of the strings\n"
                            "3 -> collapse strings to <str> and collapses numbers to a type as well.\n")

    args = parser.parse_args()
    lexed = tokenize_file(args.source_file, args.literal_handle)
    print(lexed)