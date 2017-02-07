from __future__ import print_function
from lexer import simplePyLex
import numpy as np
import tensorflow as tf

import argparse
import time
import os
from six.moves import cPickle

from utils import TextLoader
from model import Model

from six import text_type

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--save_dir', type=str, default='save',
					   help='model directory to store checkpointed models')
	parser.add_argument('--code_file', type=str, default='code.c',
					   help='code file to evaluate')

	args = parser.parse_args()
	evaluate(args)

def evaluate(args):
	with open(os.path.join(args.save_dir, 'config.pkl'), 'rb') as f:
		(saved_args, reverse_input) = cPickle.load(f)
	with open(os.path.join(args.save_dir, 'chars_vocab.pkl'), 'rb') as f:
		chars, vocab = cPickle.load(f)
	model = Model(saved_args, reverse_input, True)
	with tf.Session() as sess:
		tf.initialize_all_variables().run()
		saver = tf.train.Saver(tf.all_variables())
		ckpt = tf.train.get_checkpoint_state(args.save_dir)
		if ckpt and ckpt.model_checkpoint_path:
			saver.restore(sess, ckpt.model_checkpoint_path)
			token_list = get_tokens(args.code_file)
			vocab_token_list = convert_to_vocab_tokens(vocab, token_list, model.start_token,
				model.end_token, model.unk_token)
			probs = model.evaluate(sess, chars, vocab, vocab_token_list)
			display_results(token_list, probs)

def get_tokens(code_file):
	tmp_outfile = '/tmp/out.txt'
	simplePyLex.main(code_file, tmp_outfile, 3, "full", "True", "False")
	with open(tmp_outfile) as f:
		token_list = f.read().split(" ")
	return token_list[:-1] # Remove ending newline entry

def convert_to_vocab_tokens(vocab, token_list, start_token, end_token, unk_token):
	res = [start_token]
	for token in token_list:
		if token in vocab:
			res.append(token)
		else:
			res.append(unk_token)

	res.append(end_token)
	return res

def display_results(token_list, probs):
	for i in range(len(token_list)):
		print("{0} => {1}".format(token_list[i], probs[i]))

if __name__ == '__main__':
	main()
