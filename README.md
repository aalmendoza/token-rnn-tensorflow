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

It is assumed that you already have a corpus of code that contains space seperated tokens. Such a corpus is provided in *C_Corpus* as an example. 
Next we will need to convert this corpus into a single file that will be used as input to the language model. Below is an example of how we may do this.

```
cd source/utils
python3 create_input_from_corpus.py --corpus_dir ../../C_Corpus --out_dir ../../data/code --vocab_size 100 --train_percent .8
```

In *../../data/code* you will find the following generated files.

````
rev  test_files.txt  test.txt  test_types.txt  train_files.txt  train.txt  train_types.txt
````

Since we specified a vocbulary size of 100, in *train.txt* and *test.txt* the top 100 most frequent tokens in the corpus will appear verbatim and all other tokens will be replaced by the `<UNK>` token. A value of -1 for vocab_size indicates to make the vocabulary size equal to the number of unique tokens in the corpus.

Now we can train the model using the file *train.txt* as input. For brevity, many of the options for train.py are excluded. 

```
cd ..
python3 train.py --data_dir ../data/code
```

If we wanted to train a reverse reading language model we would instead use
```
python3 train.py --data_dir ../data/code/rev
```

After training the model, we can generate code based on the language model by running

```
python3 sample.py --data_dir ../data/code
```
