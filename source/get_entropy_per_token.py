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
	parser.add_argument('save_dir', type=str,
					   help='save directory where model checkpoints are stored')
	parser.add_argument('source', type=str,
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

	if args.pre_tokenized:
		with open(args.source, 'r') as f:
			token_list = f.read().split()
	else:
		token_list = get_tokens(args.source, args.language)
		
	token_list = convert_to_vocab_tokens(vocab, token_list, model.start_token,
		model.end_token, model.unk_token)

	with tf.Session() as sess:
		sess.run(tf.global_variables_initializer())
		saver = tf.train.Saver(tf.global_variables())
		ckpt = tf.train.get_checkpoint_state(args.save_dir)
		if ckpt and ckpt.model_checkpoint_path:
			saver.restore(sess, ckpt.model_checkpoint_path)
			entropy_list = model.get_entropy_per_token(sess, vocab, token_list)
			display_results(token_list, entropy_list)

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

def display_results(token_list, entropy_list):
	for i in range(len(entropy_list)):
		print("{0},{1}".format(token_list[i+1], entropy_list[i]))

	mean = np.mean(entropy_list)
	std = np.std(entropy_list)
	q1 = np.percentile(entropy_list, 25)
	q2 = np.percentile(entropy_list, 50)
	q3 = np.percentile(entropy_list, 75)
	print("\nMean: {0}".format(mean))
	print("Std: {0}".format(std))
	print("Q1: {0}".format(q1))
	print("Q2: {0}".format(q2))
	print("Q3: {0}".format(q3))

if __name__ == '__main__':
	main()
