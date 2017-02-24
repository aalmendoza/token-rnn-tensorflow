from __future__ import print_function
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

from pygments.lexers import get_lexer_by_name
from pygments import lex

import os.path
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
	parser.add_argument('--token_file', type=str, default='test.txt',
					   help = 'token file to find entropy values for')
	parser.add_argument('--token_type_file', type=str, default='test_types.txt',
					   help = 'token type file corresponding to the given token file')

	args = parser.parse_args()
	find_entropy_ranges(args)

def find_entropy_ranges(args):
	with open(os.path.join(args.save_dir, 'config.pkl'), 'rb') as f:
		(saved_args_fwd, reverse_input_fwd) = cPickle.load(f)
	with open(os.path.join(args.save_dir, 'chars_vocab.pkl'), 'rb') as f:
		chars_fwd, vocab_fwd = cPickle.load(f)

	model_fwd = Model(saved_args_fwd, reverse_input_fwd, True)
	with tf.Session() as sess:
		tf.initialize_all_variables().run()
		saver = tf.train.Saver(tf.all_variables())
		ckpt = tf.train.get_checkpoint_state(args.save_dir)
		if ckpt and ckpt.model_checkpoint_path:
			saver.restore(sess, ckpt.model_checkpoint_path)
			entropy_map = model_fwd.get_entropy_range_by_type(sess, chars_fwd, vocab_fwd,
				args.token_file, args.token_type_file)

			i = 1
			for key,value in entropy_map.items():
				plt.subplot(3,4,i)
				plt.boxplot(value, 0, 'gD')
				plt.title(key)
				i += 1
			plt.show()
			plt.tight_layout()
			
			# with open(os.path.join(args.save_dir, 'entropy_values.pkl'), 'wb') as f:
			# 	cPickle.dump(entropy_map, f)
			# for key, value in entropy_map.items():
			# 	print("{0} -> {1}".format(key, value))

if __name__ == '__main__':
	main()
