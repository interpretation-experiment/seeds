import re

single_letters = [u'a', u'A', u'E', u'i', u'O', u'u', u'o', u'e']
single_letter_pattern = u'|'.join(single_letters)
nucleuspattern = u'{}'.format(single_letter_pattern)
oncpattern = re.compile(u'(.*?)({})(.*)'.format(nucleuspattern))
