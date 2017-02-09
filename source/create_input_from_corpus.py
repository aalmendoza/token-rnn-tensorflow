# Creates train and test input files for the RNN LM that contain all
# of the tokens in a corpus. The corpus is assumed to contain code files
# that each are a single line and are made of space seperated tokens.

import glob
import argparse
import os.path
from sys import exit
from collections import defaultdict

UNK_TOKEN = '<UNK>'
START_TOKEN = '<START>'
EOF_TOKEN = '<EOF>'
TRAIN_FILE = 'train.txt'
TEST_FILE = 'test.txt'

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--corpus_dir', type=str, default='../C_Corpus',
	                   help='directory of corpus containing tokenized code')
	parser.add_argument('--corpus_ext', type=str, default='.c.tokens',
	                   help='extension of files in corpus')
	parser.add_argument('--out_dir', type=str, default='data/code/',
	                   help='output directory for tokenized file and logs')
	parser.add_argument('--vocab_size', type=int, default=-1,
	                   help='vocabulary size. A value of -1 corresponds to a vocabulary size equal to the number unique tokens in the corpus')
	parser.add_argument('--train_percent', type=float, default=.8,
						help='Percent of files, (0 - 1) exclusive, in corpus to use for training')

	args = parser.parse_args()
	validate_args(args)
	create_train_test_files(args.corpus_dir, args.corpus_ext, args.out_dir,
		args.vocab_size, args.train_percent)

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
	test_out_file = os.path.join(out_dir, TEST_FILE)
	create_input_file(train_files, train_out_file, vocab)
	create_input_file(test_files, test_out_file, vocab)
	create_reversed_input_file(out_dir, train_out_file, test_out_file)

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

def create_input_file(token_files, out_file, vocab):
		with open(out_file, 'w') as f:
			for token_file in token_files:
				f.write(START_TOKEN + "\n")
				with open(token_file, 'r') as tok_f:
					for token in tok_f.read().split():
						if token in vocab:
							f.write(token + "\n")
						else:
							f.write(UNK_TOKEN + "\n")
				f.write(EOF_TOKEN + "\n")

def create_reversed_input_file(out_dir, orig_train_file, orig_test_file):
	rev_dir = os.path.join(out_dir, "rev")
	rev_train = os.path.join(rev_dir, TRAIN_FILE)
	rev_test = os.path.join(rev_dir, TEST_FILE)
	os.system("mkdir {0} 2>/dev/null".format(rev_dir))
	os.system("tac {0} > {1}".format(orig_train_file, rev_train))
	os.system("tac {0} > {1}".format(orig_test_file, rev_test))

if __name__ == '__main__':
	main()