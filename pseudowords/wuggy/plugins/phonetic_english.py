# Copyright (c) 2009-2012 Emmanuel Keuleers <emmanuel.keuleers@ugent.be>
# Refactored parts of Wuggy 0.2.2b2 <http://crr.ugent.be/Wuggy>, adapted by
# Sébastien Lerique <sl@mehho.net>


from .subsyllabic_common import *


public_name = 'Phonetic English (CELEX)'
default_data = 'phonetic_english.txt'
default_neighbor_lexicon = 'phonetic_english.txt'
default_word_lexicon = 'phonetic_english.txt'
default_lookup_lexicon = 'phonetic_english.txt'
hidden_sequence = False


def transform(input_sequence, frequency=1):
    return copy_onc(input_sequence, frequency=frequency)
