import os
import sys
import re

import nltk
from django.conf import settings


MOVIE_QUOTES_PATH = os.path.dirname(__file__)
BASE_PATH = os.path.dirname(MOVIE_QUOTES_PATH)

CHARACTER = re.compile(r'\w')

SOURCE_QUOTE_PAIRS = os.path.join(
    MOVIE_QUOTES_PATH, 'moviequotes.memorable_nonmemorable_pairs.txt')
DEST_QUOTE_PAIRS = os.path.join(MOVIE_QUOTES_PATH, 'text_pairs.txt')


def read_pairs(filepath):
    """Read all pairs of memorable/nonmemorable quotes from `filepath` and
    return a list of tuples.

    Only returns the movie-matched quotes, not the quotes as they are entered
    in IMDb.

    """

    pairs = []

    with open(filepath, encoding='iso8859_15') as f:
        # Ignore first title
        f.readline()

        quote = f.readline().strip()
        while quote != '':
            memorable = ' '.join(f.readline().strip().split(' ')[1:])
            nonmemorable = ' '.join(f.readline().strip().split(' ')[1:])
            pairs.append((memorable, nonmemorable))

            # Check we're moving to the next quote
            newline = f.readline().strip()
            assert newline == ''

            # Ignore title and get next quote
            f.readline()
            quote = f.readline().strip()

    return pairs


def save_pairs(pairs, filepath):
    """Save memorable/nonmemorable quote pairs in `pairs` to `filepath`."""

    with open(filepath, 'w') as f:
        for (memorable, nonmemorable) in pairs:
            f.write(memorable + '\n')
            f.write(nonmemorable + '\n')
            f.write('\n')


def word_count(quote):
    """Count the number of words in `quote`.

    Uses the standard NLTK tokenizer, and ignores punctuation (i.e. tokens with
    no word-characters in them).

    """

    words = [token
             for sentence in nltk.tokenize.sent_tokenize(quote)
             for token in nltk.tokenize.word_tokenize(sentence)
             if CHARACTER.search(token) is not None]
    return len(words)


def valid_word_counts(pair):
    """Check if the movie-matched memorable and nonmemorable quotes in `pair`
    have the same number of words."""

    (memorable, nonmemorable) = pair
    return word_count(memorable) == word_count(nonmemorable)


def valid_pair(validator, pair):
    """Check if the movie-matched memorable and nonmemorable quotes in `pair`
    are valid for `validator`."""

    (memorable, nonmemorable) = pair
    try:
        validator(memorable)
        validator(nonmemorable)
    except:
        return False

    return True


if __name__ == '__main__':
    # Setup the environment
    sys.path.insert(1, os.path.join(BASE_PATH, 'spreadr'))

    from spreadr import settings_analysis as spreadr_settings
    from gists.validators import SpellingValidator, PunctuationValidator

    settings.configure(**spreadr_settings.__dict__)

    # Read quote pairs
    print('Reading and filtering memorable and nonmemorable quotes from {}'
          .format(SOURCE_QUOTE_PAIRS))
    pairs = read_pairs(SOURCE_QUOTE_PAIRS)

    # Filter through the pairs
    spelling_validator = SpellingValidator('english')
    punctuation_validator = PunctuationValidator()
    kept = [pair for pair in pairs
            if (valid_word_counts(pair) and
                valid_pair(spelling_validator, pair) and
                valid_pair(punctuation_validator, pair))]

    # Save the pairs we kept
    save_pairs(kept, DEST_QUOTE_PAIRS)
    print('Kept {} quote pairs out of {}, saved to {}'
          .format(len(kept), len(pairs), DEST_QUOTE_PAIRS))
