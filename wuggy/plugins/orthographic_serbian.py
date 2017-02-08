from .subsyllabic_common import *
from .orth import sr as language


public_name = 'Orhographic Serbian'
default_data = 'orthographic_serbian.txt'
default_neighbor_lexicon = 'orthographic_serbian.txt'
default_word_lexicon = 'orthographic_serbian.txt'
default_lookup_lexicon = 'orthographic_serbian.txt'


def transform(input_sequence, frequency=1):
    return pre_transform(input_sequence, frequency=frequency,
                         language=language)
