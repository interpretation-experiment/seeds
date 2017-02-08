import re

single_vowels = ['a', 'e', 'и', 'o', 'u', 'р']
nucleuspattern = '{}'.format(single_vowels)
oncpattern = re.compile('(.*?)({})(.*)'.format(nucleuspattern))
