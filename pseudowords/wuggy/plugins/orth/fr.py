# Copyright (c) 2009-2012 Emmanuel Keuleers <emmanuel.keuleers@ugent.be>
# Refactored parts of Wuggy 0.2.2b2 <http://crr.ugent.be/Wuggy>, adapted by
# Sébastien Lerique <sl@mehho.net>


import re


triple_letters = ['eai', 'iai']
double_letters = ['aa', 'au', 'ai', 'ea', 'ee', 'ia', 'ie', 'io', 'oo', 'oe',
                  'oi', 'ou', 'ui', 'ue', 'ei', 'eu', 'ae', 'oa']
single_letters = ['a', 'e', 'i', 'o', 'u', 'y']
accented_letters = [u'à', u'ê', u'è', u'é', u'â', u'ô', u'ü', u'ö']
double_accented_letters = [u'ée', u'éo', u'ué', u'éé', u'iè', u'oï']
triple_letter_pattern = '|'.join(triple_letters)
double_letter_pattern = '|'.join(double_letters)
single_letter_pattern = '|'.join(single_letters)
accented_letter_pattern = '|'.join(accented_letters)
double_accented_letter_pattern = '|'.join(double_accented_letters)
nucleuspattern = '{}|{}|{}|{}|{}'.format(triple_letter_pattern,
                                         double_accented_letter_pattern,
                                         double_letter_pattern,
                                         accented_letter_pattern,
                                         single_letter_pattern)
oncpattern = re.compile('(.*?)({})(.*)'.format(nucleuspattern))
