from __future__ import print_function
from lexer import simplePyLex
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
	parser.add_argument('--save_dir', type=str, default='save',
					   help='model directory to store checkpointed models')
	parser.add_argument('--source', type=str, default='code.c',
					   help='source file to evaluate')
	parser.add_argument('--pre_tokenized', type=str, default='false',
					   help='boolean indicating if the source file is already tokenized')

	args = parser.parse_args()
	evaluate(args)

def evaluate(args):
	pre_tokenized = str2bool(args.pre_tokenized)
	with open(os.path.join(args.save_dir, 'config.pkl'), 'rb') as f:
		(saved_args, reverse_input) = cPickle.load(f)
	with open(os.path.join(args.save_dir, 'chars_vocab.pkl'), 'rb') as f:
		chars, vocab = cPickle.load(f)
	model = Model(saved_args, reverse_input, True)
	with tf.Session() as sess:
		sess.run(tf.global_variables_initializer())
		saver = tf.train.Saver(tf.global_variables())
		ckpt = tf.train.get_checkpoint_state(args.save_dir)
		if ckpt and ckpt.model_checkpoint_path:
			saver.restore(sess, ckpt.model_checkpoint_path)
			if pre_tokenized:
				with open(args.source, 'r') as f:
					token_list = f.read().split()
			else:
				token_list = get_tokens(args.source)
				
			token_list = convert_to_vocab_tokens(vocab, token_list, model.start_token,
				model.end_token, model.unk_token)
			probs = model.evaluate(sess, chars, vocab, token_list)

def str2bool(s):
	return s.lower() in ('t', 'true', '1', 'yes')

def get_tokens(source):
	tmp_outfile = '/tmp/out.txt'
	simplePyLex.main(source, tmp_outfile, 3, "full", "True", "False")
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

if __name__ == '__main__':
	main()
