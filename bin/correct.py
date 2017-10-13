#!/usr/bin/env python

# This script will suggest fixes for an input program using a language model.

# Input: C Source Code File
# Output: A sequence of C Source Code Files

# in: 
# buggy code
# out:
# ##### FIXED
# <COMPILABLE CODE>
# ##### FIXED
# <COMPILABLE CODE>
# ##### FIXED
# <COMPILABLE CODE>
# ##### FIXED
# <COMPILABLE CODE>


from utils.lexer import simplePyLex
import argparse


# Fix Suggestions Algorithm:
# A program is a sequence of tokens.
# We need to calculate the entropy of the token wrt LM
# tokenlist = an array of tokens
# entropies = a parrallel array of entropies
# range of entropy values is 0 to infinity
# In english, entropy per letter is 4.7 bits
# In English, entropy per word is 11.82 bits


# ind

def correct(token_list, probs)
	fixed = []
	# create an index array
	i = 0
	indices = []
	for t in token_list:
		indices.append(i)
		i++

	# lowest prob => highest entropy
	bottom_probs = []
	
	
	return fixed


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('save_dir', type=str, default='save',
					   help='model directory to store checkpointed models')
	parser.add_argument('source', type=str, default='code.c',
					   help='source file to evaluate')
	parser.add_argument('--pre_tokenized', dest='pre_tokenized', action='store_true',
					   help='boolean indicating if the source file is already tokenized')
	parser.add_argument('-n', '--number', type=int, default=5,
					   help='maximum number of fix suggestions.')
	parser.set_defaults(pre_tokenized=False)

	args = parser.parse_args() #access using dot object notation 

	with open(os.path.join(args.save_dir, 'config.pkl'), 'rb') as f:
		(saved_args, reverse_input) = cPickle.load(f)
	with open(os.path.join(args.save_dir, 'token_vocab.pkl'), 'rb') as f:
		tokens, vocab = cPickle.load(f)

	model = Model(saved_args, reverse_input, True)

	if pre_tokenized:
		with open(args.source, 'r') as f:
			token_list = f.read().split()
	else:
		# tokenize code
		tokenized_code, _ = simplePyLex.tokenize_file(args.source, 3)
		token_list = tokenize_code.split()
	token_list = convert_to_vocab_tokens(vocab, token_list, model.start_token, model.end_token, model.unk_token)

	with tf.Session() as sess:
		sess.run(tf.global_variables_initializer())
		saver = tf.train.Saver(tf.global_variables())
		ckpt = tf.train.get_checkpoint_state(args.save_dir)
		if ckpt and ckpt.model_checkpoint_path:
			saver.restore(sess, ckpt.model_checkpoint_path)
			probs = model.evaluate(sess, tokens, vocab, token_list)

	fixed = correct(token_list, probs)
