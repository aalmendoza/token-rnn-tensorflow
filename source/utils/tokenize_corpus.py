import glob
import argparse
import os.path

from six.moves import cPickle
from lexer import simplePyLex
from pygments.lexers import get_lexer_by_name
from pygments import lex

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('corpus_dir', type=str,
	                   help='directory of corpus containing files to be tokenized')
	parser.add_argument('corpus_ext', type=str, default='.c',
	                   help='extension of files in corpus')
	parser.add_argument('out_dir', type=str, default='../../data/code/files',
	                   help='output directory for tokenized files')

	args = parser.parse_args()

	validate_args(args)
	tokenize_corpus(args.corpus_dir, args.corpus_ext, args.out_dir)

def validate_args(args):
	assert os.path.isdir(args.corpus_dir), "corpus_dir {0} doesn't exist".format(args.corpus_dir)
	if not os.path.isdir(args.out_dir):
		os.system("mkdir -p {0}".format(args.out_dir))

def tokenize_corpus(corpus_dir, corpus_ext, out_dir):
	corpus_files = glob.glob("{0}/*{1}".format(corpus_dir, corpus_ext))
	i = 0
	for file in corpus_files:
		tokenized_text, token_types = simplePyLex.tokenize_file(file, 3)
		tokenized_file = os.path.join(out_dir, "{0}{1}".format(i, corpus_ext))
		token_types_file = os.path.join(out_dir, "{0}{1}.types.pkl".format(i, corpus_ext))
		with open(tokenized_file, 'w') as f:
			f.write(tokenized_text)
		with open(token_types_file, 'wb') as f:
			cPickle.dump(token_types, f)

		print("{0} -> {1}".format(file, tokenized_file))
		i += 1

if __name__ == '__main__':
	main()