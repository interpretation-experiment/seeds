Gistr Seeds
===========

Source texts to be used in experimemts with the [Gistr platform](https://github.com/interpretation-experiment/gistr-app/).

The following classes of texts are gathered:

Memorable / non-memorable quote pairs
-------------------------------------

In `cornell_movie_quotes_corpus/text_pairs.txt`. Extracted from [Danescu-Niculescu-Mizil et al. (2012)](https://arxiv.org/abs/1203.6360)'s movie quotes dataset with the following commands (using the Fish shell with virtualfish and Python 3.6+):

```
git submodule update --init  # to check out the spreadr submodule

vf new -p (which python3) interpretation-experiment.seeds
pip install -r spreadr/requirements.txt

python cornell_movie_quotes_corpus/filter_quote_pairs.py
```

The `filter_quote_pairs.py` script just takes the quote pairs from the movie quotes dataset where (1) spelling is recognised, (2) punctuation is recognised, (3) the movie-matched versions have the same number of words (excluding punctuation), and saves them to `text_pairs.txt`.


Minimal narratives / series of events
-------------------------------------

In `popova/narratives.txt` and `popova/series-events.txt`. The first sentence in each of those files is taken from Forster (1927/1990), cited by Popova (2015: p. 31). The rest are all taken from Félix Fénéon, "Novels in Three Lines" (1906/2007), partly cited by Popova (2015: p. 38-39).

The classification between narrative and non-narrative (series of events) is still quite rough (at least too rough to my liking). More passes with a closer reading of Popova (2015) will be necessary.
