# Creates a single file containing all of the tokens in a corpus
# The corpus is assumed to contain code files that each are a single line
# and are made of space seperated tokens. This file will be used as input 
# to the RNN LM and will contain all unique tokens if a vocab_size of -1 is used.
# Otherwise, the vocab_size most frequent tokens in the corpus are kept
# and all other tokens are renamed to UNK_TOKEN

import glob
import argparse
from collections import defaultdict

UNK_TOKEN = '<UNK>'
START_TOKEN = '<START>'
EOF_TOKEN = '<EOF>'

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--corpus_dir', type=str, default='corpus_dir',
	                   help='directory of corpus containing tokenized code')
	parser.add_argument('--corpus_ext', type=str, default='.c.tokens',
	                   help='extension of files in corpus')
	parser.add_argument('--out_file', type=str, default='data/code/input.txt',
	                   help='output file containing all tokens in the corpus')
	parser.add_argument('--vocab_size', type=int, default=-1,
	                   help='vocabulary size. A value of -1 corresponds to a vocabulary size equal to the number unique tokens in the corpus')

	args = parser.parse_args()
	create_input_file(args.corpus_dir, args.corpus_ext, args.out_file, args.vocab_size)

def create_input_file(corpus_dir, corpus_ext, out_file, vocab_size):
	temp_token_file = '/tmp/tokens.txt'
	vocab_file = 'vocab.txt'
	total_tokens = 0
	token_freqs = defaultdict(int)
	token_files = glob.glob("{0}/*{1}".format(corpus_dir, corpus_ext))
	with open(temp_token_file, 'w') as f:
		for token_file in token_files:
			f.write(START_TOKEN + "\n")
			with open(token_file, 'r') as token_f:
				for token in token_f.read().split(" "):
					token_freqs[token] += 1
					f.write(token + "\n")
					total_tokens += 1
			f.write(EOF_TOKEN + "\n")

	vocab_tokens = sorted(token_freqs, key=token_freqs.get, reverse=True)
	if vocab_size != -1 and vocab_size < len(vocab_tokens):
		vocab_tokens = vocab_tokens[:vocab_size]
	vocab_tokens = set(vocab_tokens)
	
	with open(out_file, 'w') as f:
		with open(temp_token_file, 'r') as tmp_f:
			for line in tmp_f:
				token = line[:-1] # Trim newline character
				if token in vocab_tokens or token == START_TOKEN or token == EOF_TOKEN:
					f.write(token + "\n")
				else:
					f.write(UNK_TOKEN + "\n")

if __name__ == '__main__':
	main()