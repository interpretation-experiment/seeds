import re
import os
import argparse
import itertools
import csv
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


def apply_shape(target, word):
    """Return `word` shaped like `target` in terms of upper- and lowercase
    letters."""

    assert len(target) == len(word)
    return ''.join([wc.upper() if tc.isupper() else wc
                    for (tc, wc) in zip(target, word.lower())])


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


argparser = argparse.ArgumentParser(description='Generate jabberwocky '
                                    'sentences from reference sentences')
argparser.add_argument('sentences', metavar='SENTENCE', nargs='*',
                       help='sentences to use as reference. Required if no '
                       'reference file is provided through --reference '
                       '(added to sentences in the --reference file '
                       'otherwise).')
argparser.add_argument('--reference', metavar='REFERENCE_FILE',
                       type=argparse.FileType(), default=[],
                       help='a file containing reference sentences, '
                       'one per line (empty lines are ignored). Required '
                       'if no sentences are provided on the command line.')
argparser.add_argument('--out', metavar='OUT_FILE',
                       type=argparse.FileType('w'), default=None,
                       help='a file to output generated sentences to, '
                       'in csv format, with suggested pseudowords. '
                       'If not provided, output is printed to stdout.')


def print_status(message, out):
    if out is None:
        # We're printing generated results to stdout, so we add some formatting
        # so as not to pollute the output
        message = '\x1b[2K\r' + bcolors.LOW + message + bcolors.ENDC
    print(message, end='' if out is None else None)


def append(current, part, out, format=''):
    if out is None:
        # We're printing generated results to stdout, so we add some colours
        part = format + part + bcolors.ENDC
    current.append(part)


if __name__ == '__main__':
    args = argparser.parse_args()
    outwriter = csv.writer(args.out) if args.out is not None else None

    # Check we got at least one sentence
    if len(args.sentences) == 0 and args.reference == []:
        argparser.print_help()
        quit()

    # Load spaCy
    print_status('Loading spaCy...', args.out)
    nlp = spacy.load('en')
    test_text_targets(nlp)

    # Load Wuggy
    print_status('Loading Wuggy...', args.out)
    wuggy = Generator()
    wuggy_path = os.path.abspath(os.path.dirname(generator.__file__))
    wuggy.data_path = os.path.join(wuggy_path, 'data')
    wuggy.load(orthographic_english)
    wuggy_options = wuggy.default_options()
    pseudo_count = 10
    print_status('', args.out)

    for text in itertools.chain(args.sentences, args.reference):
        text = normalize(text)
        if len(text) == 0:
            continue

        doc = nlp(text)
        targets = text_targets(doc)

        # Generate all pseudowords
        all_pseudowords = []
        for target in targets:
            segments = wuggy.lookup(target.orth_.lower())

            while segments is None:
                segments = input("Couldn't determine a segmentation for '" +
                                 bcolors.BOLD + target.orth_ + bcolors.ENDC +
                                 "', please enter one yourself: ").lower()
                if segments.replace('-', '').lower() != target.orth_.lower():
                    print("Your entry doesn't match the target word when "
                          "converting back. Please try again.")
                    segments = None

            target_pseudowords = \
                [apply_shape(target.orth_, w)
                 for (_, w) in wuggy.run(wuggy_options, segments, '')]
            # Pad missing words with spaces
            target_pseudowords += ([' ' * len(target.orth_)] *
                                   (pseudo_count - len(target_pseudowords)))
            all_pseudowords.append(target_pseudowords)

        # Collect sentence parts, with colours if we're printing to stdout
        last_end = 0
        line = []
        for target in targets:
            start, end = span(target)
            assert target.orth_ == text[start:end]
            append(line, text[last_end:start], args.out)
            append(line, target.orth_, args.out,
                   bcolors.BOLD + bcolors.OKGREEN)
            last_end = end
        append(line, text[last_end:], args.out)

        # Actually print to stdout or to the out file
        if args.out is None:
            print(''.join(line))
        else:
            outwriter.writerow(line)

        # Collect candidate pseudowords for each target
        for i in range(pseudo_count):
            pseudowords = [target_pseudowords[i]
                           for target_pseudowords in all_pseudowords]
            last_end = 0
            line = []
            for target, pseudoword in zip(targets, pseudowords):
                start, end = span(target)
                assert end - start == len(pseudoword)
                append(line, ' ' * (start - last_end), args.out)
                append(line, pseudoword, args.out, bcolors.OKBLUE)
                last_end = end
            append(line, '', args.out)

            # Actually print to stdout or to the out file
            if args.out is None:
                print(''.join(line))
            else:
                outwriter.writerow(line)

    if args.out is not None:
        print('All done!')
