import glob
import argparse
import os.path

from lexer import simplePyLex
from pygments.lexers import get_lexer_by_name
from pygments import lex

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--corpus_dir', type=str, default='../../C_Corpus',
	                   help='directory of corpus containing files to be tokenized')
	parser.add_argument('--corpus_ext', type=str, default='.c',
	                   help='extension of files in corpus')
	parser.add_argument('--out_dir', type=str, default='../../data/code/files',
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
		tokenized_text = simplePyLex.tokenize_file(file, 3)
		tokenized_file = "{0}/{1}{2}".format(out_dir, i, corpus_ext)
		with open(tokenized_file, 'w') as f:
			f.write(tokenized_text)

		print(i)
		i += 1

if __name__ == '__main__':
	main()