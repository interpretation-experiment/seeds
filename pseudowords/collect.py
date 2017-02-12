import argparse
import csv


argparser = argparse.ArgumentParser(description='Collect jabberwocky '
                                    'sentences from a processed suggestion '
                                    'csv file')
argparser.add_argument('infile', metavar='IN_FILE',
                       type=str,
                       help='a csv file containing processed sentence '
                       'suggestions (as output by `generate.py`), '
                       'one per line (empty lines are ignored)')
argparser.add_argument('outfile', metavar='OUT_FILE',
                       type=argparse.FileType('w'),
                       help='a file to output collected sentences to')


if __name__ == '__main__':
    args = argparser.parse_args()

    with open(args.infile) as infile:
        inreader = csv.reader(infile)

        n_texts = 0
        for parts in inreader:
            text = ''.join(parts).strip()
            if len(text) > 0:
                n_texts += 1
                args.outfile.write(text + '\n')

    print("All done! Collected {} texts.".format(n_texts))
