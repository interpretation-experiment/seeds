from .subsyllabic_common import *
from .phon import fr as language


public_name = 'Phonetic French'
default_data = 'phonetic_french.txt'
default_neighbor_lexicon = 'phonetic_french.txt'
default_word_lexicon = 'phonetic_french.txt'
default_lookup_lexicon = 'phonetic_french.txt'


def transform(input_sequence, frequency=1):
    return pre_transform(input_sequence, frequency=frequency,
                         language=language)