# Copyright (c) 2009-2012 Emmanuel Keuleers <emmanuel.keuleers@ugent.be>
# Refactored parts of Wuggy 0.2.2b2 <http://crr.ugent.be/Wuggy>, adapted by
# Sébastien Lerique <sl@mehho.net>


import re


single_vowels = ['a', 'e', 'i', 'o', 'u', 'r']
nucleuspattern = '{}'.format(single_vowels)
oncpattern = re.compile('(.*?)({})(.*)'.format(nucleuspattern))
