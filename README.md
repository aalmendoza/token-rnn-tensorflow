# token-rnn-tensorflow


## Dependencies

* python-3.4.3 (may work for previous version)
* pygments
  * sudo pip3 install pygments
* numpy

## Overview

Creates a single input for the RNN from a pre-tokenized corpus of C (or any
programming language) files.

````
python3 create_input_from_corpus.py
````

`create_input_from_corpus.py` accepts optional arguments.  When you run without arguments, you are running these defaults:

````
python3 create_input_from_corpus.py --corpus_dir ../C_Corpus --corpus_ext .c.tokens --vocab_size -1 --train_percent 0.8 --out_dir data/code
````

In *data/code* you will find the generated files.

````
marvelez@jarvis:~/github/token-rnn-tensorflow/source$ ls data/code/
rev  test_files.txt  test.txt  test_types.txt  train_files.txt  train.txt  train_types.txt
````

The data/code/train.txt file is fed to the LSTM.

````
marvelez@jarvis:~/github/token-rnn-tensorflow/source$ head data/code/train.txt 
<START>
static
char
error
[
<int>
]
;
static
off_t
````





