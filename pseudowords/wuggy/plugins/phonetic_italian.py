# Copyright (c) 2009-2012 Emmanuel Keuleers <emmanuel.keuleers@ugent.be>
# Refactored parts of Wuggy 0.2.2b2 <http://crr.ugent.be/Wuggy>, adapted by
# Sébastien Lerique <sl@mehho.net>


from .subsyllabic_common import *
from .phon import it as language


public_name = 'Phonetic Italian'
default_data = 'phonetic_italian.txt'
default_neighbor_lexicon = 'phonetic_italian.txt'
default_word_lexicon = 'phonetic_italian.txt'
default_lookup_lexicon = 'phonetic_italian.txt'


def transform(input_sequence, frequency=1):
    return pre_transform(input_sequence, frequency=frequency,
                         language=language)
