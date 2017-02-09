# Copyright (c) 2009-2012 Emmanuel Keuleers <emmanuel.keuleers@ugent.be>
# Refactored parts of Wuggy 0.2.2b2 <http://crr.ugent.be/Wuggy>, adapted by
# Sébastien Lerique <sl@mehho.net>


import re


single_letters = [u'a', u'A', u'E', u'i', u'O', u'u', u'o', u'e']
single_letter_pattern = u'|'.join(single_letters)
nucleuspattern = u'{}'.format(single_letter_pattern)
oncpattern = re.compile(u'(.*?)({})(.*)'.format(nucleuspattern))
