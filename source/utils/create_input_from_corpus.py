import glob
import argparse
import os.path
from math import ceil
from six.moves import cPickle
from collections import defaultdict

UNK_TOKEN = '<UNK>'
START_TOKEN = '<START>'
END_TOKEN = '<EOF>'
TRAIN_FILE = 'train.txt'
TEST_FILE = 'test.txt'
VALID_FILE = 'valid.txt'
TRAIN_TYPE_FILE = 'train_types.txt'
TEST_TYPE_FILE = 'test_types.txt'
VALID_TYPE_FILE = 'valid_types.txt'

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('corpus_dir', type=str,
	                   help='directory of corpus containing pre-tokenized files')
	parser.add_argument('corpus_ext', type=str, default='.c',
	                   help='extension of files in corpus')
	parser.add_argument('out_dir', type=str,
	                   help='output directory for tokenized file and logs')
	parser.add_argument('train_percent', type=float, default=.7,
						help='percent of files, (0 - 1] inclusive, in corpus to use for training')
	parser.add_argument('valid_percent', type=float, default=.15,
					   	help='percent of files, [0 - 1] inclusive, in corpus to use for validation')
	parser.add_argument('test_percent', type=float, default=.15,
					   	help='percent of files, [0 - 1] inclusive, in corpus to use for testing')
	parser.add_argument('--vocab_size', type=int, default=-1,
	                   help='vocabulary size. A value of -1 corresponds to a vocabulary size equal to the number unique tokens in the corpus')	
	parser.add_argument('--import_vocab_from', type=str,
						help='Path to save directory that allows you to use a pre existing vocabulary')

	args = parser.parse_args()

	validate_args(args)
	if args.import_vocab_from is not None:
		vocab = load_vocab(args.import_vocab_from)
		token_files = glob.glob("{0}/*{1}".format(args.corpus_dir, args.corpus_ext))
		token_out_file = os.path.join(args.out_dir, "input.txt")
		token_types_out_file = os.path.join(args.out_dir, "input_types.txt")
		create_input_file(token_files, token_out_file, token_types_out_file, vocab)
	else:
		create_train_test_files(args)

def validate_args(args):
	assert (args.train_percent > 0 and args.train_percent <= 1), "train_percent must be in the range (0, 1] inclusive"
	assert (args.valid_percent >= 0 and args.valid_percent <= 1), "valid_percent must be in the range [0, 1] inclusive"
	assert (args.test_percent >= 0 and args.test_percent <= 1), "test_percent must be in the range [0, 1] inclusive"
	assert (args.train_percent + args.valid_percent + args.test_percent == 1), "percentage splits must add up to 1"
	assert os.path.isdir(args.corpus_dir), "corpus_dir {0} doesn't exist".format(args.corpus_dir)
	if not os.path.isdir(args.out_dir):
		os.system("mkdir {0}".format(args.out_dir))

def load_vocab(save_dir):
	assert os.path.isdir(save_dir)," %s must be a a path" % save_dir
	assert os.path.isfile(os.path.join(save_dir,"token_vocab.pkl")),"token_vocab.pkl.pkl file does not exist in path %s" % save_dir
	with open(os.path.join(save_dir, 'token_vocab.pkl'), 'rb') as f:
		chars, vocab = cPickle.load(f)
	return vocab

def create_train_test_files(args):
	token_files = glob.glob("{0}/*{1}".format(args.corpus_dir, args.corpus_ext))
	[train_files, valid_files, test_files] = split_files(token_files, args.train_percent,
		args.valid_percent, args.test_percent)
	use_valid_file = len(valid_files) > 0
	use_test_file = len(test_files) > 0
	log_file_split(train_files, valid_files, test_files, args.out_dir)

	vocab = get_vocab(train_files, args.vocab_size)
	create_vocab_files(train_files, args.out_dir, TRAIN_FILE, TRAIN_TYPE_FILE, vocab)
	if use_valid_file:
		create_vocab_files(valid_files, args.out_dir, VALID_FILE, VALID_TYPE_FILE, vocab)
	if use_test_file:
		create_vocab_files(test_files, args.out_dir, TEST_FILE, TEST_TYPE_FILE, vocab)

	create_reversed_input_file(args.out_dir, use_valid_file, use_test_file)

# Split the files into train, validation, and test
# Note that each percent desinates the splits for the files
# in the corpus but not the number of tokens in each split
# This is noteworthy as some token files contain significantly
# more tokens than others so the number of tokens in each split
# may not entirely represent the percents given
def split_files(token_files, train_percent, valid_percent, test_percent):
	num_train_files = int(train_percent * len(token_files))
	num_valid_files = ceil(valid_percent * len(token_files))
	num_test_files = len(token_files) - num_train_files - num_valid_files
	train_files = token_files[:num_train_files]
	valid_files = token_files[num_train_files:num_train_files + num_valid_files]
	test_files = token_files[num_train_files + num_valid_files:]
	return [train_files, valid_files, test_files]

# Log the file paths used for the train, validation, and test splits
def log_file_split(train_files, valid_files, test_files, out_dir):
	train_file_log = os.path.join(out_dir, "train_files.txt")
	log_files(train_file_log, train_files)
	if len(valid_files) > 0:
		valid_file_log = os.path.join(out_dir, "valid_files.txt")
		log_files(valid_file_log, valid_files)
	if len(test_files) > 0:
		test_file_log = os.path.join(out_dir, "test_files.txt")
		log_files(test_file_log, test_files)


def log_files(output_file, file_names):
	with open(output_file, 'w') as log_file:
		for file in file_names:
			log_file.write(file + "\n")

def get_vocab(token_files, vocab_size):
	total_tokens = 0
	token_freqs = defaultdict(int)
	
	for token_file in token_files:
		with open(token_file, 'r') as f:
			tokens = f.read().split()
			for token in tokens:
				token_freqs[token] += 1
				total_tokens += 1

	return create_vocab(token_freqs, vocab_size)

# Limit the vocaulary to the specified vocab size
def create_vocab(token_freqs, vocab_size):
	vocab_tokens = sorted(token_freqs, key=token_freqs.get, reverse=True)
	if vocab_size != -1 and vocab_size < len(vocab_tokens):
		vocab_tokens = vocab_tokens[:vocab_size]
	vocab_tokens = set(vocab_tokens)
	return vocab_tokens

# Write tokenized file using the specified vocab as well as the corresponding
# token types
def create_vocab_files(token_files, out_dir, token_file_name, token_type_file_name, vocab):
	token_out_file = os.path.join(out_dir, token_file_name)
	token_type_out_file = os.path.join(out_dir, token_type_file_name)	

	with open(token_out_file, 'w') as token_out, open(token_type_out_file, 'w') as token_type_out:
		for token_file in token_files:
			token_type_file = token_file + ".types.pkl"
			with open(token_type_file, 'rb') as f:
				token_types = cPickle.load(f)

			token_out.write(START_TOKEN + "\n")
			token_type_out.write('START_TOKEN' + "\n")
			with open(token_file, 'r') as tok_f:
				i = 0
				for line in tok_f:
					tokens = line.split()
					for token in tokens:
						token_type_out.write(token_types[i] + "\n")
						i += 1
						if token in vocab:
							token_out.write(token + " ")
						else:
							token_out.write(UNK_TOKEN + " ")
					token_out.write("\n")			

			token_out.write(END_TOKEN + "\n")
			token_type_out.write("END_TOKEN" + "\n")

def create_reversed_input_file(out_dir, use_valid_file, use_test_file):
	rev_dir = os.path.join(out_dir, "rev")
	os.system("mkdir {0} 2>/dev/null".format(rev_dir))

	reverse_files(TRAIN_FILE, TRAIN_TYPE_FILE, out_dir, rev_dir)
	if use_valid_file:
		reverse_files(VALID_FILE, VALID_TYPE_FILE, out_dir, rev_dir)
	if use_test_file:
		reverse_files(TEST_FILE, TEST_TYPE_FILE, out_dir, rev_dir)

def reverse_files(token_file_name, token_type_file_name, out_dir, rev_dir):
	orig_token_file = os.path.join(out_dir, token_file_name)
	orig_token_type_file = os.path.join(out_dir, token_type_file_name)
	rev_token_file = os.path.join(rev_dir, token_file_name)
	rev_token_type_file = os.path.join(rev_dir, token_type_file_name)
	reverse_file(orig_token_file, rev_token_file)
	reverse_file(orig_token_type_file, rev_token_type_file)

def reverse_file(src, dest):
	os.system("tac {0} > {1}".format(src, dest))

if __name__ == '__main__':
	main()