import re
import sys
import os
# The readline module works with `input` by simply importint it, so we disable
# linting with flake8 for this line
import readline  # noqa

import spacy
from wuggy import generator
from wuggy.generator import Generator
from wuggy.plugins import orthographic_english


DOUBLE_SPACES = re.compile(r' {2,}')


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    LOW = '\033[2m'


def span(token):
    """Get the span of `token` in its document."""
    return (token.idx, token.idx + len(token.orth_))


def orth_spans(tokens):
    """Extract orthography and spans from a list of tokens."""
    return [(token.orth_, span(token)) for token in tokens]


def normalize(text):
    """Remove double spaces in `text` and strip it (returning the normalized
    version)."""
    return DOUBLE_SPACES.sub(' ', text.strip())


def text_targets(doc):
    """List the tokens to be replaced by pseudowords in `doc`."""

    targets = []

    for i, token in enumerate(doc):
        if token.tag_[:2] not in ['NN', 'JJ', 'VB', 'RB']:
            # Not a content word
            continue
        if token.dep_ == 'aux' and token.head.pos_ == 'VERB':
            # Auxiliary verb => not a content word
            continue
        if token.dep_ == 'neg' and token.pos_ == 'ADV':
            # Negation => not a content word
            continue
        if not token.is_alpha:
            # Non-alphabetic characters
            continue
        if i > 0:
            prev_tag, prev_end = doc[i - 1].tag_, span(doc[i - 1])[1]
            if prev_tag[0].isalpha() and prev_end == span(token)[0]:
                # The previous token is a word and is stuck to us, so we're in
                # a contraction
                continue
        if i < len(doc) - 1:
            next_tag, next_start = doc[i + 1].tag_, span(doc[i + 1])[0]
            if next_tag[0].isalpha() and next_start == span(token)[1]:
                # The next token is a word and is stuck to us, so we're in a
                # contraction
                continue
        targets.append(token)

    return targets


def test_text_targets(nlp):
    assert orth_spans(text_targets(
        nlp("We haven't seen each other since high school."))) == \
            [('seen', (11, 15)),
             ('other', (21, 26)),
             ('high', (33, 37)),
             ('school', (38, 44))]
    assert orth_spans(text_targets(
        nlp("We have not seen each other since high school."))) == \
        [('seen', (12, 16)),
         ('other', (22, 27)),
         ('high', (34, 38)),
         ('school', (39, 45))]
    assert orth_spans(text_targets(
        nlp("Don't piss me off, junior.  "
            "Or I will repaint this office with your brains."))) == \
        [('piss', (6, 10)),
         ('junior', (19, 25)),
         ('repaint', (38, 45)),
         ('office', (51, 57)),
         ('brains', (68, 74))]
    assert orth_spans(text_targets(
        nlp("Do not piss me off, junior.  "
            "Or I will repaint this office with your brains."))) == \
        [('piss', (7, 11)),
         ('junior', (20, 26)),
         ('repaint', (39, 46)),
         ('office', (52, 58)),
         ('brains', (69, 75))]


if __name__ == '__main__':
    # Use by giving your input sentences as arguments:
    # python pseudowords/generate.py "This is a sentence." "And another."

    # Load spaCy
    print(bcolors.LOW + 'Loading spaCy' + bcolors.ENDC)
    nlp = spacy.load('en')
    test_text_targets(nlp)

    # Load Wuggy
    print(bcolors.LOW + 'Loading Wuggy' + bcolors.ENDC)
    wuggy = Generator()
    wuggy_path = os.path.abspath(os.path.dirname(generator.__file__))
    wuggy.data_path = os.path.join(wuggy_path, 'data')
    wuggy.load(orthographic_english)
    wuggy_options = wuggy.default_options()
    pseudo_count = 10

    for line in sys.argv[1:]:
        line = normalize(line)
        doc = nlp(line)
        targets = text_targets(doc)

        # Generate all pseudowords
        print(bcolors.LOW + 'Generating pseudowords' + bcolors.ENDC)
        all_pseudowords = []
        for target in targets:
            segments = wuggy.lookup(target.orth_)
            if segments is None:
                segments = input("Couldn't determine a segmentation for '" +
                                 bcolors.BOLD + target.orth_ + bcolors.ENDC +
                                 "', please enter one yourself: ")
            target_pseudowords = \
                [w for (_, w) in wuggy.run(wuggy_options, segments, '')]
            # Pad missing words with spaces
            target_pseudowords += ([' ' * len(target.orth_)] *
                                   (pseudo_count - len(target_pseudowords)))
            all_pseudowords.append(target_pseudowords)

        # Print the actual sentence with target words highlighted
        last_end = 0
        for target in targets:
            start, end = span(target)
            assert target.orth_ == line[start:end]
            print(line[last_end:start], end='')
            print(bcolors.BOLD + bcolors.OKGREEN + target.orth_ + bcolors.ENDC,
                  end='')
            last_end = end
        print(line[last_end:])

        # Print candidate pseudowords for each target
        for i in range(pseudo_count):
            pseudowords = [target_pseudowords[i]
                           for target_pseudowords in all_pseudowords]
            last_end = 0
            for target, pseudoword in zip(targets, pseudowords):
                start, end = span(target)
                assert end - start == len(pseudoword)
                print(' ' * (start - last_end), end='')
                print(bcolors.OKBLUE + pseudoword + bcolors.ENDC, end='')
                last_end = end
            print()
