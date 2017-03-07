Gistr Seeds
===========

Source texts to be used in experimemts with the [Gistr platform](https://github.com/interpretation-experiment/gistr-app/).


Environment setup
-----------------

Using the Fish shell with virtualfish and Python 3.6+:

```
git submodule update --init  # to check out the spreadr submodule

vf new -p (which python3) interpretation-experiment.seeds

pip install -r spreadr/requirements.txt
python -m nltk.downloader punkt averaged_perceptron_tagger

pip install -r pseudowords/requirements.txt
python -m spacy.en.download all
```


Seed list
---------

The following classes of texts are gathered:


### Memorable / non-memorable quote pairs

In `cornell_movie_quotes_corpus/text_pairs.txt`. Extracted from [Danescu-Niculescu-Mizil et al. (2012)](https://arxiv.org/abs/1203.6360)'s movie quotes dataset with the following command (after setting up the environment by following the instructions above):

```
python cornell_movie_quotes_corpus/filter_quote_pairs.py
```

The `filter_quote_pairs.py` script just takes the quote pairs from the movie quotes dataset where (1) spelling is recognised, (2) punctuation is recognised, (3) the movie-matched versions have the same number of words (excluding punctuation), and saves them to `text_pairs.txt`.

From that, the following files are extracted:
* `text_pairs_30.txt` -- the first 30 text pairs with no offensive words
* `text_pairs-25random_10+w_noexpletives.txt` -- a random sample of 25 text pairs:
  * with at least 10 words in each sentence.
  * with no offensive words or connotations (excluding expletives and hand-checking),
  * hand-checked so that memorable and non-memorable pairs have about the same number of characters (not only same number of words); pairs with length problems (only one) were replaced with a hand-picked pair satisfying the above conditions
* `text_pairs-15to16words.txt` -- the 27 text pairs with 15 or 16 words


### Minimal narratives / series of events

In `popova/narratives.txt` and `popova/series-events.txt`. The first sentence in each of those files is taken from Forster (1927/1990), cited by Popova (2015: p. 31). The rest are all taken from Félix Fénéon, "Novels in Three Lines" (1906/2007), partly cited by Popova (2015: p. 38-39).

The classification between narrative and non-narrative (series of events) is still quite rough (at least too rough to my liking). More passes with a closer reading of Popova (2015) will be necessary.


### The above, with pseudowords

We also convert part of the above sources to jabberwocky sentences, using Keuleers & Brysbaert's [Wuggy](http://crr.ugent.be/programs-data/wuggy). The generated sentences are in:

* `cornell_movie_quotes_corpus/text_pairs_30-pseudowords.txt` (based on `cornell_movie_quotes_corpus/text_pairs_30.txt`)
* `popova/narratives-pseudowords.txt`
* `popova/series-events-pseudowords.txt`

These are generated with the following two steps (in the environment set up above):

```
python pseudowords/generate.py --out pseudoword-suggestions.csv --reference reference-file.txt
```

to identify which words should be replaced in each sentence in `reference-file.txt` and have Wuggy generate suggestions for each of them. Then open the `csv` file in a spreadsheet editor, and for each sentence, do the actual pseudoword picking and replacement, removing all unused suggestions. This leaves you with jabberwocky sentences split into cells, and empty rows (where the suggestions were before removal). If the result is saved to `pseudoword-suggestions-processed.csv`, then:

```
python pseudowords/collect.py pseudoword-suggestions-processed.csv reference-pseudowords.txt
```

will collect all the jabberwocky sentences you generated into `reference-pseudowords.txt`, one sentence per line. This is how the jabberwocky files in `cornell_movie_quotes_corpus/` and `popova/` are created (those files are then re-spaced to show sentence pairs or improve readability).


#### Note on choosing pseudowords

The following word classes are targeted for replacement:

* All nouns
* All adjectives
* Verbs that are not auxiliaries, modals, or copulas
* Adverbs that are not negations

With the following notes:

* Don't replace any proper nouns or words starting with a capital letter
* Repeated words or stems (e.g. a verb repeated but conjugated differently) are replaced with different pseudowords (i.e. the commonality is not maintained)
* No words involved in contractions are replaced, except genitives. E.g. in "the *dog*'s *tail*", both *dog* and *tail* get replaced -- this is done by manually using Wuggy (as the `pseudowords/generate.py` script ignores all contractions) to generate suggestions for *dogs* (with the "s"), then picking pseudowords with a final "s" and separating it off again.
* Composed words (e.g. "mother-in-law") are replaced, similarly to genitives, by sticking all parts together and re-separating them in the generated pseudowords (this is also done manually, since `pseudowords/generate.py` considers composed words to be contractions and therefore ignores them)

We use the default Wuggy settings to generate 10 suggestions for each target word. Picking a pseudoword among those 10 suggestions is done by trying to maintain the following:

* When possible, keep the original word's inflection (verb conjugation, plural, noun-like, adverb-like, etc.)
* If we can't do the above, try re-running Wuggy pseudoword generation (with the same settings) to see if the other random pseudowords allow it; if still not possible, go with one of those generated pseudowords anyway
* Try to choose a pseudoword that doesn't evoke the original word, so simple sentences can't be inferred back

Language being what it is, i.e. so complex, added to the fact we used realistic sentences (instead of hand-generated sentences that don't present any border cases), target selection and pseudoword generation is not flawless. If anything, it is sometimes a bit approximate: some words that should have been targets were likely overlooked, and some words that shouldn't have been replaced were replaced.

I can only say the above rules reflect my attempt at replacing the *content words* of sentences to a reasonable extent, knowing that it's not always clear where content is in a given sentence.
