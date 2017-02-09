# Copyright (c) 2009-2012 Emmanuel Keuleers <emmanuel.keuleers@ugent.be>
# Refactored parts of Wuggy 0.2.2b2 <http://crr.ugent.be/Wuggy>, adapted by
# Sébastien Lerique <sl@mehho.net>


import re


double_letters = ['aa', 'ea', 'ee', 'ia', 'ie', 'io(?!u)', 'oo', 'oe', 'ou',
                  '(?<!q)ui(?=.)', 'ei', 'eu', 'ae', 'ey(?=.)', 'oa']
single_letters = ['a', 'e', 'i(?!ou)', 'o', '(?<!q)u', 'y(?![aeiou])']
accented_letters = [u'à', u'ê', u'è', u'é', u'â', u'ô', u'ü']
double_letter_pattern = '|'.join(double_letters)
single_letter_pattern = '|'.join(single_letters)
accented_letter_pattern = '|'.join(accented_letters)
nucleuspattern = '{}|{}|{}'.format(double_letter_pattern,
                                   accented_letter_pattern,
                                   single_letter_pattern)
oncpattern = re.compile('(.*?)({})(.*)'.format(nucleuspattern))
