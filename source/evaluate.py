from __future__ import print_function
from utils.lexer import simplePyLex
import numpy as np
import tensorflow as tf

import argparse
import time
import os
from six.moves import cPickle

from utils.text_loader import TextLoader
from model import Model

from six import text_type

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('save_dir', type=str, default='save',
					   help='model directory to store checkpointed models')
	parser.add_argument('source', type=str, default='code.c',
					   help='source file to evaluate')
	parser.add_argument('language', type=str, default='C',
					   help='programming language of source file')
	parser.add_argument('--pre_tokenized', action="store_true",
					   help='boolean indicating if the source file is already tokenized. use this argument if using the test file that was automatically created')

	args = parser.parse_args()
	evaluate(args)

def evaluate(args):
	with open(os.path.join(args.save_dir, 'config.pkl'), 'rb') as f:
		(saved_args, reverse_input) = cPickle.load(f)
	with open(os.path.join(args.save_dir, 'token_vocab.pkl'), 'rb') as f:
		tokens, vocab = cPickle.load(f)
	model = Model(saved_args, reverse_input, True)
	with tf.Session() as sess:
		sess.run(tf.global_variables_initializer())
		saver = tf.train.Saver(tf.global_variables())
		ckpt = tf.train.get_checkpoint_state(args.save_dir)
		if ckpt and ckpt.model_checkpoint_path:
			saver.restore(sess, ckpt.model_checkpoint_path)
			if args.pre_tokenized:
				with open(args.source, 'r') as f:
					token_list = f.read().split()
			else:
				token_list = get_tokens(args.source, args.language)
				
			token_list = convert_to_vocab_tokens(vocab, token_list, model.start_token,
				model.end_token, model.unk_token)
			probs = model.evaluate(sess, tokens, vocab, token_list)

def get_tokens(source, language):
	tokenized_code, _ = simplePyLex.tokenize_file(source, language)
	return tokenized_code.split()

def convert_to_vocab_tokens(vocab, token_list, start_token, end_token, unk_token):
	res = []
	if token_list[0] != start_token:
		res.append(start_token)

	for token in token_list:
		if token in vocab:
			res.append(token)
		else:
			res.append(unk_token)

	if token_list[-1] != end_token:
		res.append(end_token)
	return res

if __name__ == '__main__':
	main()
