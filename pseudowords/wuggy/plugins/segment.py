# Copyright (c) 2009-2012 Emmanuel Keuleers <emmanuel.keuleers@ugent.be>
# Refactored parts of Wuggy 0.2.2b2 <http://crr.ugent.be/Wuggy>, adapted by
# Sébastien Lerique <sl@mehho.net>


class SegmentationError(Exception):

    """Occurs when an input string cannot be segmented"""

    pass


def onsetnucleuscoda(orthographic_syllable, lang=None):
    oncpattern = lang.oncpattern
    m = oncpattern.match(orthographic_syllable)

    try:
        return [m.group(1), m.group(2), m.group(3)]
    except AttributeError:
        raise SegmentationError('Input syllable could not be segmented')
