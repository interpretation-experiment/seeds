from .subsyllabic_common import *
from .orth import de as language


public_name = 'Orthographic German'
default_data = 'orthographic_german.txt'
default_neighbor_lexicon = 'orthographic_german.txt'
default_word_lexicon = 'orthographic_german.txt'
default_lookup_lexicon = 'orthographic_german.txt'


def transform(input_sequence, frequency=1):
    return pre_transform(input_sequence, frequency=frequency,
                         language=language)