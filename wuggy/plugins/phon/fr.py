import re

single_vowels = ['a', 'i', 'y', 'u', 'o', 'O', 'e', 'E', '°', '2', '9', '5',
                 '1', '@', '§', '3']
nucleuspattern = '{}'.format(single_vowels)
oncpattern = re.compile('(.*?)({})(.*)'.format(nucleuspattern))
