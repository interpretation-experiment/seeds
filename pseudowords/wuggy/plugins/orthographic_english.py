from .subsyllabic_common import *
from .orth import en as language


public_name = 'Orthographic English'
default_data = 'orthographic_english.txt'
default_neighbor_lexicon = 'orthographic_english.txt'
default_word_lexicon = 'orthographic_english.txt'
default_lookup_lexicon = 'orthographic_english.txt'


def transform(input_sequence, frequency=1):
    return pre_transform(input_sequence, frequency=frequency,
                         language=language)
