from __future__ import print_function
from lexer import simplePyLex
import numpy as np
import tensorflow as tf

import argparse
import time
import os
from six.moves import cPickle

from pygments.lexers import get_lexer_by_name
from pygments import lex

from utils import TextLoader
from model import Model

from six import text_type

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--save_dir', type=str, default='save',
					   help='model directory to store checkpointed models')
	parser.add_argument('--source', type=str, default='code.c',
					   help='source code to attempt to fix')
	parser.add_argument('--dest', type=str, default='code.c',
					   help='path to file containing possible fix of source')

	args = parser.parse_args()
	try_fix(args)

def try_fix(args):
	with open(os.path.join(args.save_dir, 'config.pkl'), 'rb') as f:
		saved_args, reverse_input = cPickle.load(f)
	with open(os.path.join(args.save_dir, 'chars_vocab.pkl'), 'rb') as f:
		chars, vocab = cPickle.load(f)
	with open(os.path.join(args.save_dir, 'entropy_values.pkl'), 'rb') as f:
		entropy_map = cPickle.load(f)
	model = Model(saved_args, reverse_input, True)
	with tf.Session() as sess:
		tf.initialize_all_variables().run()
		saver = tf.train.Saver(tf.all_variables())
		ckpt = tf.train.get_checkpoint_state(args.save_dir)
		if ckpt and ckpt.model_checkpoint_path:
			saver.restore(sess, ckpt.model_checkpoint_path)
			token_list = get_tokens(args.source)
			vocab_token_list, unk_tokens = convert_to_vocab_tokens(vocab, token_list, model.start_token,
				model.end_token, model.unk_token)
			token_types = get_token_types(vocab_token_list, model.start_token, model.end_token,
				model.unk_token)
			tokens = model.try_fix(sess, chars, vocab, vocab_token_list, token_types,
				entropy_map)

			# Also need to sub back <int>, <float>, <str>, etc
			tokens = convert_unk_tokens_back(tokens, unk_tokens, model.unk_token)

			for token in tokens:
				print(token, end=' ')
			print("")

			# side_by_side(vocab_token_list[1:], tokens)

def get_tokens(code_file):
	tmp_outfile = '/tmp/out.txt'
	simplePyLex.main(code_file, tmp_outfile, 3, "full", "True", "False")
	with open(tmp_outfile) as f:
		token_list = f.read().split(" ")
	return token_list[:-1] # Remove ending newline entry

def get_token_types(tokens, start_token, end_token, unk_token):
	token_types = []
	lexer = get_lexer_by_name('C')
	for token in tokens:
		if token == unk_token:
			token_types.append("Token.Name")
		elif token == start_token:
			token_types.append('START_TOKEN')
		elif token == end_token:
			token_types.append('EOF_TOKEN')
		else:
			res = lex(token, lexer)
			token_type = str(list(res)[0][0])
			token_types.append(token_type)
	return token_types

def convert_to_vocab_tokens(vocab, token_list, start_token, end_token, unk_token):
	res = [start_token]
	unk_tokens = []
	for token in token_list:
		if token in vocab:
			res.append(token)
		else:
			res.append(unk_token)
			unk_tokens.append(token)

	res.append(end_token)
	return res, unk_tokens

def convert_unk_tokens_back(tokens, unk_tokens, unk_token):
	res = []
	i = 0
	for token in tokens:
		if token == unk_token:
			res.append(unk_tokens[i])
			i += 1
		else:
			res.append(token)
	return res

def side_by_side(orig_tokens, new_tokens):
	for i in range(len(orig_tokens)):
		print("{0} -> {1}".format(orig_tokens[i], new_tokens[i]))

if __name__ == '__main__':
	main()
