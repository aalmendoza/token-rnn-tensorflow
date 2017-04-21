# token-rnn-tensorflow
Token level LSTM language model for any given tokenized code corpus. 

## Dependencies

* python-3.4.3 (may work for previous version)
* pygments
  * sudo pip3 install Pygments
* numpy
  * sudo pip3 install numpy
* Tensorflow 1.0.0
  * sudo pip3 install tensorflow

## Getting Started

Before training the language model on a code corpus, it is necessary to tokenize the code first. Assuming that the corpus is located the directory *corpus_dir* and contains C code files, this can be achieved by the following

```
cd source
python3 utils/tokenize_corpus.py corpus_dir ".c" ../data/example/files
```

Doing so will store the tokenized files of the corpus in the directory *../data/example/files*. Next we will need to convert this tokenized corpus into a single file that will be used as input to the language model. Following our example, this is done by

```
python3 utils/create_input_from_corpus.py ../data/example/files/ ".c" ../data/example/ .7 .15 .15 --vocab_size 100
```

Running this command will split the corpus into 70% training data, 15% validation data, and 15% testing data as well as produce the RNN LM input file for each set. In addition, the corresponding token types and the files used in each split are logged. Note to check all of the arguments by passing -h to *utils/create_input_from_corpus.py*. In *../../data/example* you will find the following generated files.

````
files           test.txt         train.txt        valid.txt
rev             test_types.txt   train_types.txt  valid_types.txt
test_files.txt  train_files.txt  valid_files.txt
````

Since we specified a vocbulary size of 100, in *train.txt*, *valid.txt*, and *test.txt* the top 100 most frequent tokens in the corpus will appear verbatim and all other tokens will be replaced by the `<UNK>` token. A value of -1 for vocab_size indicates to make the vocabulary size equal to the number of unique tokens in the corpus.

Now we can train the model using the file *train.txt* as input. For brevity, many of the options for train.py are excluded. 

```
python3 train.py ../data/example/ ../save/example
```

If we wanted to train a reverse reading language model we would instead use

```
python3 train.py ../data/example/rev ../save/example/rev
```

After training the model, we can generate code based on the language model by running

```
python3 sample.py ../save/example
```
