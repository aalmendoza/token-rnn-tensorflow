# Creates train and test input files for the RNN LM that contain all
# of the tokens in a corpus. The corpus is assumed to contain code files
# that each are a single line and are made of space seperated tokens.

import glob
import argparse
import os.path
from six.moves import cPickle
from sys import exit
from collections import defaultdict

from pygments.lexers import get_lexer_by_name
from pygments import lex

UNK_TOKEN = '<UNK>'
START_TOKEN = '<START>'
END_TOKEN = '<EOF>'
TRAIN_FILE = 'train.txt'
TEST_FILE = 'test.txt'
TEST_TYPE_FILE = 'test_types.txt'
TRAIN_TYPE_FILE = 'train_types.txt'

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--corpus_dir', type=str, default='../../C_Corpus',
	                   help='directory of corpus containing tokenized code')
	parser.add_argument('--corpus_ext', type=str, default='.c.tokens',
	                   help='extension of files in corpus')
	parser.add_argument('--out_dir', type=str, default='../../data/code/',
	                   help='output directory for tokenized file and logs')
	parser.add_argument('--vocab_size', type=int, default=-1,
	                   help='vocabulary size. A value of -1 corresponds to a vocabulary size equal to the number unique tokens in the corpus')
	parser.add_argument('--train_percent', type=float, default=.8,
						help='Percent of files, (0 - 1) exclusive, in corpus to use for training')
	parser.add_argument('--import_vocab_from', type=str,
						help='Optional argument that allows you to use a pre existing vocabulary from a save directory')

	args = parser.parse_args()

	validate_args(args)
	if args.import_vocab_from is not None:
		vocab = load_vocab(args.import_vocab_from)
		token_files = glob.glob("{0}/*{1}".format(args.corpus_dir, args.corpus_ext))
		token_out_file = os.path.join(args.out_dir, "input.txt")
		token_types_out_file = os.path.join(args.out_dir, "input_types.txt")
		create_input_file(token_files, token_out_file, token_types_out_file, vocab)
	else:
		create_train_test_files(args.corpus_dir, args.corpus_ext, args.out_dir,
			args.vocab_size, args.train_percent)

def load_vocab(save_dir):
	assert os.path.isdir(save_dir)," %s must be a a path" % save_dir
	assert os.path.isfile(os.path.join(save_dir,"chars_vocab.pkl")),"chars_vocab.pkl.pkl file does not exist in path %s" % save_dir
	with open(os.path.join(save_dir, 'chars_vocab.pkl'), 'rb') as f:
		chars, vocab = cPickle.load(f)
	return vocab

def validate_args(args):
	assert (args.train_percent > 0 and args.train_percent < 1), "train_percent must be in the range (0, 1) exclusive"
	assert os.path.isdir(args.corpus_dir), "corpus_dir {0} doesn't exist".format(args.corpus_dir)
	if not os.path.isdir(args.out_dir):
		os.system("mkdir {0}".format(args.out_dir))

def create_train_test_files(corpus_dir, corpus_ext, out_dir, vocab_size, train_percent):
	token_files = glob.glob("{0}/*{1}".format(corpus_dir, corpus_ext))
	[train_files, test_files] = split_files(token_files, train_percent)
	log_file_split(train_files, test_files, out_dir)

	vocab = get_vocab(train_files, vocab_size)
	train_out_file = os.path.join(out_dir, TRAIN_FILE)
	train_type_out_file = os.path.join(out_dir, TRAIN_TYPE_FILE)
	test_out_file = os.path.join(out_dir, TEST_FILE)
	test_type_out_file = os.path.join(out_dir, TEST_TYPE_FILE)
	create_input_file(train_files, train_out_file, train_type_out_file, vocab)
	create_input_file(test_files, test_out_file, test_type_out_file, vocab)
	create_reversed_input_file(out_dir)

def split_files(token_files, train_percent):
	num_train_files = int(train_percent * len(token_files))
	num_test_files = len(token_files) - num_train_files
	train_files = token_files[:num_train_files]
	test_files = token_files[num_train_files:]
	return [train_files, test_files]

def log_file_split(train_files, test_files, out_dir):
	train_file_log = os.path.join(out_dir, "train_files.txt")
	test_file_log = os.path.join(out_dir, "test_files.txt")
	log_files(train_file_log, train_files)
	if len(test_files) > 0:
		log_files(test_file_log, test_files)

def log_files(output_file, file_names):
	with open(output_file, 'w') as log_file:
		for file in file_names:
			log_file.write(file + "\n")

def get_vocab(token_files, vocab_size):
	total_tokens = 0
	token_freqs = defaultdict(int)
	
	for token_file in token_files:
		with open(token_file, 'r') as token_f:
			for token in token_f.read().split():
				token_freqs[token] += 1
				total_tokens += 1

	return create_vocab(token_freqs, vocab_size)

def create_vocab(token_freqs, vocab_size):
	vocab_tokens = sorted(token_freqs, key=token_freqs.get, reverse=True)
	if vocab_size != -1 and vocab_size < len(vocab_tokens):
		vocab_tokens = vocab_tokens[:vocab_size]
	vocab_tokens = set(vocab_tokens)
	return vocab_tokens

# Try to lex in batches
def create_input_file(token_files, token_out_file, token_type_out_file, vocab):
	lexer = get_lexer_by_name('C')
	with open(token_out_file, 'w') as token_out, open(token_type_out_file, 'w') as token_type_out:
		for token_file in token_files:
			token_out.write(START_TOKEN + "\n")
			token_type_out.write('START_TOKEN' + "\n")
			with open(token_file, 'r') as tok_f:
				tokens = tok_f.read().split()
				# token_types = get_token_types(tokens, lexer)
				for token in tokens:
					token_type_out.write(get_token_type(lexer, token) + "\n")
					if token in vocab:
						token_out.write(token + "\n")
					else:
						token_out.write(UNK_TOKEN + "\n")
			token_out.write(END_TOKEN + "\n")
			token_type_out.write("END_TOKEN" + "\n")

def get_token_type(lexer, token):
	if token == START_TOKEN:
		return 'START_TOKEN'
	elif token == END_TOKEN:
		return 'END_TOKEN'
	elif token == UNK_TOKEN:
		return 'Token.Name'
	elif token == '<int>':
		return 'Token.Literal.Number.Integer'
	elif token == '<float>':
		return 'Token.Literal.Number.Float'
	elif token == '<oct>':
		return 'Token.Literal.Number.Oct'
	elif token == '<bin>':
		return 'Token.Literal.Number.Bin'
	elif token == '<hex>':
		return 'Token.Literal.Number.Hex'
	elif token == '<num>':
		return 'Token.Literal.Number'
	elif token == '<str>':
		return 'Token.Literal.String'
	else:
		res = lex(token, lexer)
		return str(list(res)[0][0])

def create_reversed_input_file(out_dir):
	orig_train_file = os.path.join(out_dir, TRAIN_FILE)
	orig_train_type_file = os.path.join(out_dir, TEST_TYPE_FILE)
	orig_test_file = os.path.join(out_dir, TEST_FILE)
	orig_test_type_file = os.path.join(out_dir, TEST_TYPE_FILE)
	rev_dir = os.path.join(out_dir, "rev")
	rev_train = os.path.join(rev_dir, TRAIN_FILE)
	rev_test = os.path.join(rev_dir, TEST_FILE)
	rev_test_type = os.path.join(rev_dir, TEST_TYPE_FILE)
	os.system("mkdir {0} 2>/dev/null".format(rev_dir))
	os.system("tac {0} > {1}".format(orig_train_file, rev_train))
	os.system("tac {0} > {1}".format(orig_test_file, rev_test))
	os.system("tac {0} > {1}".format(orig_test_type_file, rev_test_type))

if __name__ == '__main__':
	main()