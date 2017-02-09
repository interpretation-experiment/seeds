# Copyright (c) 2009-2012 Emmanuel Keuleers <emmanuel.keuleers@ugent.be>
# Refactored parts of Wuggy 0.2.2b2 <http://crr.ugent.be/Wuggy>, adapted by
# Sébastien Lerique <sl@mehho.net>


from collections import namedtuple


Sequence = namedtuple('Sequence', ['representation', 'frequency'])


def compute_difference(gen_stat, ref_stat):
    if isinstance(gen_stat, (tuple, list)):
        return [gen_stat[i] - ref_stat[i]
                for i in range(min(len(gen_stat), len(ref_stat)))]
    elif isinstance(gen_stat, dict):
        return dict((i, gen_stat[i] - ref_stat[i])
                    for i in range(len(gen_stat)))
    elif isinstance(gen_stat, (float, int)):
        return gen_stat - ref_stat


def compute_match(gen_stat, ref_stat):
    return gen_stat == ref_stat


def difference(function):
    function.difference = compute_difference
    return function


def match(function):
    function.match = compute_match
    return function
