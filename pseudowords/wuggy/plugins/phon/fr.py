# Copyright (c) 2009-2012 Emmanuel Keuleers <emmanuel.keuleers@ugent.be>
# Refactored parts of Wuggy 0.2.2b2 <http://crr.ugent.be/Wuggy>, adapted by
# Sébastien Lerique <sl@mehho.net>


import re


single_vowels = ['a', 'i', 'y', 'u', 'o', 'O', 'e', 'E', '°', '2', '9', '5',
                 '1', '@', '§', '3']
nucleuspattern = '{}'.format(single_vowels)
oncpattern = re.compile('(.*?)({})(.*)'.format(nucleuspattern))
