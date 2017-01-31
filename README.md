Gistr Seeds
===========

Source texts to be used in experimemts with the [Gistr platform](https://github.com/interpretation-experiment/gistr-app/).

The following classes of texts are gathered:

Memorable / non-memorable quote pairs
-------------------------------------

In `cornell_movie_quotes_corpus/text_pairs.txt`. Extracted from [Danescu-Niculescu-Mizil (2012)](https://arxiv.org/abs/1203.6360)'s movie quotes dataset with the following commands (using the Fish shell with virtualfish and Python 3.6+):

```
git submodule update --init  # to check out the spreadr submodule

vf new -p (which python3) interpretation-experiment.seeds
pip install -r spreadr/requirements.txt

python cornell_movie_quotes_corpus/filter_quote_pairs.py
```

The `filter_quote_pairs.py` script just takes the quote pairs from the movie quotes dataset where (1) spelling is recognised, (2) punctuation is recognised, (3) the movie-matched versions have the same number of words (excluding punctuation), and saves them to `text_pairs.txt`.


Minimal narratives / series of facts
------------------------------------

In `feneon/texts.txt`. TODO
