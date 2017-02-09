# Copyright (c) 2009-2012 Emmanuel Keuleers <emmanuel.keuleers@ugent.be>
# Refactored parts of Wuggy 0.2.2b2 <http://crr.ugent.be/Wuggy>, adapted by
# Sébastien Lerique <sl@mehho.net>


import re
import time
import types
import codecs
from fractions import Fraction
from collections import defaultdict

from .bigramchain import BigramChain


class Generator:

    def __init__(self):
        self.data_path = 'data'
        self.bigramchain = None
        self.bigramchains = {}
        self.attribute_subchain = None
        self.frequency_subchain = None
        self.segmentset_subchain = None
        self.reference_sequence = None
        self.frequency_filter = None
        self.segmentset_filter = None
        self.current_sequence = None
        self.output_mode = None
        self.attribute_filters = {}
        self.statistics = {}
        self.word_lexicon = defaultdict(list)
        self.neighbor_lexicon = []
        self.reference_statistics = {}
        self.stat_cache = {}
        self.sequence_cache = []
        self.difference_statistics = {}
        self.match_statistics = {}
        self.lookup_lexicon = {}
        self.status = {'message': '', 'progress': 0}
        self.subscribers = []

    def set_status(self, message, progress):
        for receiver in [self]+self.subscribers:
            receiver.status['message'] = message
            receiver.status['progress'] = progress

    def clear_status(self):
        for receiver in [self]+self.subscribers:
            receiver.status['message'] = ''
            receiver.status['progress'] = 0

    def load(self, plugin_module, data_file=None, size=100, cutoff=1,
             token=False):
        if plugin_module.__name__ not in self.bigramchains:
            if data_file is None:
                path = u"%s/%s" % (self.data_path, plugin_module.default_data)
                data_file = codecs.open(
                    path, 'r', plugin_module.default_encoding)

            self.bigramchains[plugin_module.__name__] = \
                BigramChain(plugin_module)
            self.bigramchains[plugin_module.__name__].subscribers.append(self)
            self.bigramchains[plugin_module.__name__].load(
                data_file, size=size, cutoff=cutoff, token=token)
        self.activate(plugin_module.__name__)

    def activate(self, name):
        if isinstance(name, types.ModuleType):
            name = name.__name__

        self.bigramchain = self.bigramchains[name]
        self.plugin_module = self.bigramchain.plugin_module
        self.load_neighbor_lexicon()
        self.load_word_lexicon()
        self.load_lookup_lexicon()

    def load_word_lexicon(self, data_file=None, cutoff=0):
        if data_file is None:
            path = "{}/{}".format(self.data_path,
                                  self.plugin_module.default_word_lexicon)
            data_file = codecs.open(path, 'r',
                                    self.plugin_module.default_encoding)

        self.word_lexicon = defaultdict(list)
        lines = data_file.readlines()
        nlines = float(len(lines))

        for i, line in enumerate(lines):
            if i % 1000 == 0:
                self.set_status('Loading Word Lexicon', i / nlines*100)

            fields = line.strip().split('\t')
            word = fields[0]
            frequency_per_million = fields[-1]

            # BUGFIX
            # this was
            # `if float(frequency_per_million) > cutoff:`
            # which in Python 3 gives
            # TypeError: '>' not supported between instances of 'str' and 'int'
            # and in Python 2 always evaluates to True
            if float(frequency_per_million) >= cutoff:
                self.word_lexicon[word[0], len(word)].append(word)

        data_file.close()
        self.clear_status()

    def load_neighbor_lexicon(self, data_file=None, cutoff=1):
        if data_file is None:
            path = "{}/{}".format(self.data_path,
                                  self.plugin_module.default_neighbor_lexicon)
            data_file = codecs.open(path, 'r',
                                    self.plugin_module.default_encoding)

        self.neighbor_lexicon = []
        lines = data_file.readlines()
        nlines = float(len(lines))

        for i, line in enumerate(lines):
            if i % 1000 == 0:
                self.set_status('Loading Neighbor Lexicon', i/nlines*100)

            fields = line.strip().split('\t')
            word = fields[0]
            frequency_per_million = fields[-1]

            # BUGFIX
            # this was
            # `if float(frequency_per_million) > cutoff:`
            # which in Python 3 gives
            # TypeError: '>' not supported between instances of 'str' and 'int'
            # and in Python 2 always evaluates to True
            if float(frequency_per_million) >= cutoff:
                self.neighbor_lexicon.append(word)

        data_file.close()
        self.clear_status()

    def load_lookup_lexicon(self, data_file=None):
        self.lookup_lexicon = {}

        if data_file is None:
            path = "{}/{}".format(self.data_path,
                                  self.plugin_module.default_lookup_lexicon)
            data_file = codecs.open(path, 'r',
                                    self.plugin_module.default_encoding)

        lines = data_file.readlines()
        nlines = float(len(lines))

        for i, line in enumerate(lines):
            if i % 1000 == 0:
                self.set_status('Loading Segmentation Lookup Lexicon',
                                i / nlines * 100)

            fields = line.strip().split(self.plugin_module.separator)
            reference, representation = fields[0:2]
            self.lookup_lexicon[reference] = representation

        data_file.close()
        self.clear_status()

    def lookup(self, reference):
        return self.lookup_lexicon.get(reference, None)

    def list_attributes(self):
        return self.plugin_module.Segment._fields

    def list_default_attributes(self):
        return self.plugin_module.default_fields

    def set_reference_sequence(self, sequence):
        self.reference_sequence = \
            self.plugin_module.transform(sequence).representation
        self.reference_sequence_frequencies = \
            self.bigramchain.get_frequencies(self.reference_sequence)

        # clear all statistics related to previous reference sequences
        self.clear_stat_cache()

        # compute the reference sequence's lexical statistics
        for name in self.list_statistics():
            function = eval("self.plugin_module.statistic_%s" % (name))
            self.reference_statistics[name] = \
                function(self, self.reference_sequence)

        # # set the default attributes
        # for attribute in self.list_default_attributes():
        #     self.set_attribute_filter(attribute,self.reference_sequence)

    def get_limit_frequencies(self, fields):
        limits = []

        if tuple(fields) not in self.bigramchain.limit_frequencies:
            self.bigramchain.build_limit_frequencies(fields)

        for i in range(0, len(self.reference_sequence) - 1):
            subkey_a = (i, tuple([self.reference_sequence[i]
                                  .__getattribute__(field)
                                  for field in fields]))
            subkey_b = (i + 1, tuple([self.reference_sequence[i + 1]
                                      .__getattribute__(field)
                                      for field in fields]))
            subkey = (subkey_a, subkey_b)

            try:
                limits.append(self.bigramchain
                              .limit_frequencies[tuple(fields)][subkey])
            except:
                limits.append[{max: 0, min: 0}]

        return limits

    def list_statistics(self):
        names = [name for name in dir(self.plugin_module)
                 if name.startswith('statistic')]
        return [name.replace('statistic_', '') for name in names]

    def set_statistic(self, name):
        self.statistics[name] = None

    def set_statistics(self, names):
        for name in names:
            self.statistics[name] = None

    def set_all_statistics(self):
        self.set_statistics(self.list_statistics())

    def apply_statistics(self, sequence=None):
        if sequence is None:
            sequence = self.current_sequence

        for name in self.statistics:
            function = eval("self.plugin_module.statistic_%s" % (name))
            if (sequence, name) in self.stat_cache:
                self.statistics[name] = self.stat_cache[(sequence, name)]
            else:
                self.statistics[name] = function(self, sequence)
                self.stat_cache[(sequence, name)] = self.statistics[name]

            # compute matching and difference statistics
            if hasattr(function, 'match'):
                self.match_statistics[name] = \
                    function.match(self.statistics[name],
                                   self.reference_statistics[name])
            if hasattr(function, 'difference'):
                self.difference_statistics[name] = \
                    function.difference(self.statistics[name],
                                        self.reference_statistics[name])

    def clear_statistics(self):
        self.statistics = {}

    def clear_stat_cache(self):
        self.stat_cache = {}

    def clear_sequence_cache(self):
        self.sequence_cache = []

    def list_output_modes(self):
        names = [name for name in dir(self.plugin_module)
                 if name.startswith('output')]
        return [name.replace('output_', '') for name in names]

    def set_output_mode(self, name):
        self.output_mode = eval("self.plugin_module.output_%s" % (name))

    def set_attribute_filter(self, name, reference_sequence=None):
        if reference_sequence is None:
            reference_sequence = self.reference_sequence

        self.attribute_filters[name] = reference_sequence
        self.attribute_subchain = None

    def set_attribute_filters(self, names, reference_sequence=None):
        for name in names:
            self.set_attribute_filter(
                name, reference_sequence=reference_sequence)

    def apply_attribute_filters(self):
        for attribute, reference_sequence in self.attribute_filters.items():
            subchain = (self.attribute_subchain
                        if self.attribute_subchain is not None
                        else self.bigramchain)
            self.attribute_subchain = \
                subchain.attribute_filter(reference_sequence, attribute)

    def clear_attribute_filters(self):
        self.attribute_filters = {}

    def clear_attribute_filter(self, name):
        del self.attribute_filters[name]

    def set_frequency_filter(self, lower, upper, kind='dev',
                             reference_sequence=None):
        if reference_sequence is None:
            reference_sequence = self.reference_sequence
        self.frequency_filter = (reference_sequence, lower, upper, kind)

    def clear_frequency_filter(self):
        self.frequency_filter = None
        self.frequency_subchain = None

    def apply_frequency_filter(self):
        reference_sequence, lower, upper, kind = self.frequency_filter
        subchain = (self.attribute_subchain
                    if self.attribute_subchain is not None
                    else self.bigramchain)
        self.frequency_subchain = \
            subchain.frequency_filter(reference_sequence, lower, upper, kind)

    def set_segmentset_filter(self, segmentset):
        if type(segmentset) != set:
            segmentset = set(segmentset)
        self.segmentset_filter = segmentset

    def clear_segmentset_filter(self):
        self.segmentset_filter = None
        self.segmentset_subchain = None

    def apply_segmentset_filter(self):
        segmentset = self.segmentset_filter

        if self.frequency_subchain is not None:
            subchain = self.frequency_subchain
        elif self.attribute_subchain is not None:
            subchain = self.attribute_subchain
        else:
            subchain = self.bigramchain

        self.segmentset_subchain = \
            subchain.segmentset_filter(self.reference_sequence, segmentset)

    def clear_filters(self):
        self.clear_attribute_filters()
        self.clear_frequency_filter()

    def generate(self, clear_cache=True):
        if clear_cache:
            self.clear_sequence_cache()

        if self.output_mode is None:
            output_mode = self.plugin_module.output_pass
        else:
            output_mode = self.output_mode

        if (len(self.attribute_filters) == 0
                and self.frequency_subchain is None
                and self.segmentset_subchain is None):
            subchain = self.bigramchain

        if len(self.attribute_filters) != 0:
            if self.attribute_subchain is None:
                self.apply_attribute_filters()
            subchain = self.attribute_subchain

        if self.frequency_filter is not None:
            self.apply_frequency_filter()
            subchain = self.frequency_subchain

        if self.segmentset_filter is not None:
            self.apply_segmentset_filter()
            subchain = self.segmentset_subchain

        if self.reference_sequence is not None:
            subchain = subchain.clean(len(self.reference_sequence) - 1)
            subchain.set_startkeys(self.reference_sequence)
        else:
            subchain.set_startkeys()

        for sequence in subchain.generate():
            if (self.plugin_module.output_plain(sequence)
                    in self.sequence_cache):
                pass
            else:
                self.sequence_cache.append(
                    self.plugin_module.output_plain(sequence))
                self.current_sequence = sequence
                self.apply_statistics()
                yield output_mode(sequence)

    def run(self, options, reference_sequence, match_expression):
        # Clear previous results
        self.clear_sequence_cache()
        self.clear_statistics()
        self.clear_filters()

        # Get some general options
        self.maxtime = int(options['search_time'])
        self.maxcandidates = int(options['ncandidates'])

        # Which statistics were required by the user?
        statistics = ('lexicality', 'old20', 'ned1', 'overlap_ratio')
        active_statistics = [stat for stat in statistics if options[stat]]

        # Set the reference sequence
        self.set_reference_sequence(reference_sequence)

        # Set segment length filter if required
        if options['match_segment_length']:
                self.set_attribute_filters(('segment_length',))

        # Some options require computation of statistics
        required_statistics = []
        if options['overlapping_segments']:
            required_statistics.append('overlap_ratio')
        if options['output_type'] != 'Both':
            required_statistics.append('lexicality')
        if options['maxdeviation']:
            required_statistics.append('transition_frequencies')
        if (not options['match_segment_length']
                and options['match_plain_length']):
            required_statistics.append('plain_length')
        self.set_statistics(required_statistics)

        # Set output mode (also transform reference sequence if necessary)
        if options['output_mode'] == "Syllables":
            self.set_output_mode('syllabic')
        elif options['output_mode'] == "Segments":
            self.set_output_mode('segmental')
        else:
            self.set_output_mode('plain')
            reference_sequence = reference_sequence.replace(u'-', '')

        # Compile the matching expression if required (matching is always done
        # on specified output mode!)
        if len(match_expression) > 0:
            regex = re.compile(match_expression)

        # Initialize variables for the main loop
        exponent = 1  # Frequency matching exponent
        self.ncandidates = 0
        self.nchecked = 0
        self.starttime = time.time()
        self.stopgenerator = False
        outputs = []

        # The while loop is only relevant for concentric search
        while True:
            if self.stopgenerator or self.elapsed_time > self.maxtime:
                break

            if options['concentric']:
                self.set_frequency_filter(2 ** exponent, 2 ** exponent)
                exponent = exponent + 1

            # This is the loop where the main work is done
            # as concentric search would always find the same sequences
            # we have to keep the found sequences in a cache
            for sequence in self.generate(clear_cache=False):
                # Break if required
                if self.stopgenerator:
                    break

                # Matching routine
                # Initially, match is True (since all conditions have
                # to be fulfilled we can reject on one False)
                match = True
                overlap_ratio = Fraction(int(options['overlap_numerator']),
                                         int(options['overlap_denominator']))
                if (options['overlapping_segments'] and
                        self.statistics['overlap_ratio'] != overlap_ratio):
                    match = False
                if (not options['match_segment_length'] and
                        options['match_plain_length'] and
                        self.difference_statistics['plain_length'] != 0):
                    match = False
                if (options['output_type'] == 'Only pseudowords'
                        and self.statistics['lexicality'] == 'W'):
                    match = False
                if (options['output_type'] == 'Only words'
                        and self.statistics['lexicality'] == 'N'):
                    match = False
                if len(match_expression) > 0 and regex.match(sequence) is None:
                    match = False

                # What to do if we found a matching candidate
                if match:
                    self.ncandidates = self.ncandidates + 1

                    # Compute statistics required only for output
                    for statistic in active_statistics:
                        self.set_statistic(statistic)
                    self.apply_statistics()

                    # Prepare the output
                    output = []

                    # Append reference sequence and generated sequence (always)
                    output.append(reference_sequence)
                    output.append(sequence)

                    # Append all required statistics
                    for statistic in active_statistics:
                        output.append(self.statistics[statistic])
                        if statistic in ['old20', 'ned1']:
                            output.append(
                                self.difference_statistics[statistic])

                    # Compute maximal deviation statistic if required
                    if options['maxdeviation']:
                        differences = \
                            self.difference_statistics[
                                'transition_frequencies']
                        maxindex, maxdev = \
                            max(differences.items(), key=lambda x: abs(x[1]))
                        sumdev = sum((abs(d) for d in differences.values()))

                        # Maximal deviation
                        output.append(maxdev)

                        # Summed deviation
                        output.append(sumdev)

                        # The maximally deviating transition
                        segments = [element.letters
                                    for element in self.current_sequence]
                        visual = segments
                        visual[maxindex] = "[{}".format(visual[maxindex])
                        visual[maxindex + 1] = \
                            "{}]".format(visual[maxindex + 1])
                        output.append("".join(visual)
                                      .replace('^', '_')
                                      .replace('$', '_'))

                    # Save output
                    outputs.append(output)

                # Make sure only required statistics are computed on the next
                # yield
                self.clear_statistics()
                self.set_statistics(required_statistics)
                self.nchecked = self.nchecked + 1
                if (self.elapsed_time >= self.maxtime
                        or self.ncandidates >= self.maxcandidates):
                    self.stopgenerator = True

        if not options['concentric']:
            self.stopgenerator = True

        return outputs

    def default_options(self):
        options = {}
        options['output_type'] = 'Only pseudowords'
        options['output_mode'] = 'Plain'
        options['ncandidates'] = '10'
        options['search_time'] = '10'
        options['match_segment_length'] = True
        options['match_plain_length'] = True
        options['concentric'] = True
        options['overlapping_segments'] = True
        options['overlap_numerator'] = '2'
        options['overlap_denominator'] = '3'
        options['lexicality'] = False
        options['old20'] = False
        options['ned1'] = False
        options['overlap_ratio'] = False
        options['maxdeviation'] = False

        return options

    @property
    def elapsed_time(self):
        return time.time() - self.starttime
