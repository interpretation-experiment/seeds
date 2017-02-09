import re

single_vowels = ['a', 'e', 'i', 'o', 'u', 'r']
nucleuspattern = '{}'.format(single_vowels)
oncpattern = re.compile('(.*?)({})(.*)'.format(nucleuspattern))
