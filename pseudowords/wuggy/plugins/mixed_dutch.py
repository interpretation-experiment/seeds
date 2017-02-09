# Copyright (c) 2009-2012 Emmanuel Keuleers <emmanuel.keuleers@ugent.be>
# Refactored parts of Wuggy 0.2.2b2 <http://crr.ugent.be/Wuggy>, adapted by
# Sébastien Lerique <sl@mehho.net>


from .subsyllabic_common import *


public_name = 'Mixed Dutch'
default_data = 'mixed_dutch.txt'
default_neighbor_lexicon = 'mixed_dutch.txt'
default_word_lexicon = 'mixed_dutch.txt'
default_lookup_lexicon = 'mixed_dutch.txt'
hidden_sequence = True


def transform(input_sequence, frequency=1):
    return copy_onc_hidden(input_sequence, frequency=frequency)
