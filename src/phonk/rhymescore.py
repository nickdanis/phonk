import cmudict
import re
import pkgutil, io
import pandas as pd
from itertools import zip_longest, chain
from collections import defaultdict

class RhymeComp:
    feature_file = pkgutil.get_data(__name__,"data/hayes.csv")
    diffs_file = pkgutil.get_data(__name__,"data/diffs.csv")
    feature_table = pd.read_csv(io.BytesIO(feature_file),index_col=0)
    diffs = pd.read_csv(io.BytesIO(diffs_file),index_col=0)
    cmu = cmudict.dict()
    vowel = re.compile(r'.*\d')
    arpa_dict = {'AY' : 'aɪ',
            'D' : 'd',
            'IY' : 'i',
            'V' : 'v',
            'AE' : 'æ',
            'JH' : 'd͡ʒ',
            'UH' : 'ʊ',
            'T' : 't',
            'Y' : 'j',
            'AH' : 'ʌ',
            'G' : 'ɡ',
            'Z' : 'z',
            'P' : 'p',
            'TH' : 'θ',
            'M' : 'm',
            'R' : 'ɹ',
            'K' : 'k',
            'EH' : 'ɛ',
            'EY' : 'eɪ',
            'NG' : 'ŋ',
            'ZH' : 'ʒ',
            'HH' : 'h',
            'SH' : 'ʃ',
            'OY' : 'ɔɪ',
            'S' : 's',
            'AO' : 'ɔ',
            'F' : 'f',
            'W' : 'w',
            'IH' : 'ɪ',
            'DH' : 'ð',
            'L' : 'l',
            'N' : 'n',
            'CH' : 't͡ʃ',
            'AA' : 'ɑ',
            'B' : 'b',
            'OW' : 'oʊ',
            'UW' : 'u',
            'AW' : 'aʊ',
            'ER' : 'ɹ̩'}

    def __init__(self, raw_w1, raw_w2, 
                    e_comp = 6, # score for empty positions
                    syllables = 1 # number of syllables for the rhyme,
                    ):
        self.raw_pair = (raw_w1, raw_w2)
        self.e_comp = e_comp
        self.syllables = syllables
        self.possible_prons = []
        self.prons = self.get_pron()
        self.best_pair = self.rhyme_score()
        self.score = self.best_pair[2]

    def get_pron(self):
        '''gets arpabet representation for each word given
        if word is a string, it pulls from CMU
        if otherwise, it assumes it is already in ARPA bet'''
        prons_list = []
        for word in self.raw_pair:
            if isinstance(word, str):
                prons_list.append(RhymeComp.cmu.get(word))
            else:
                prons_list.append([word])
        return prons_list


    def get_rhyme(self,pron):
        '''takes a arbabet list pronunciation, returns the final VC* sequence as a list'''
        rhyme = []
        i = 0
        vowel_count = len([v for v in pron if RhymeComp.vowel.match(v)])
        limit = min(self.syllables, vowel_count)
        #if len(vowel.findall(pron)) > self.syllables,
        for seg in pron[::-1]:
            rhyme.append(seg)
            if RhymeComp.vowel.match(seg):
                i += 1
                if i == limit:
                    break
        return rhyme[::-1]

    def add_none(self, seq):
        '''takes a list seq and adds None at all possible positions'''
        return [seq[:i] + [None] + seq[i:] for i in range(len(seq)+1)]

    def add_nones(self, seq, nones):
        '''takes int nones and add this many None items to a list seq in all possible positions'''
        combos = defaultdict(list)
        combos[0] = [seq]
        for i in range(nones):
            combos[i+1].extend(chain(*[self.add_none(seq) for seq in combos[i]]))
        return {tuple(seq) for seq in combos[nones]}

    def diff_score(self, seq1, seq2):
        '''takes two lists, compares each segment based on featural differences
        score for None comparison is 6, arbitrary value'''
        diff = []
        for comp in zip_longest(seq1,seq2):
            if None not in comp:
                diff.append(RhymeComp.diffs.loc[comp[0][:2],comp[1][:2]])
            else:
                diff.append(self.e_comp)
        return sum(diff)

    def align_score(self, seq1, seq2):
        '''takes two sequences. if the sequences are of different length, 
        None is added at every possible position. the lowest scoring pair,
        and the score, is returned as a tuple'''
        if len(seq1) != len(seq2):
            short = min([seq1, seq2], key=len)
            long = max([seq1, seq2], key=len)
        else:
            long = seq1
            short = seq2
        align_scores = dict()
        for align in self.add_nones(short, len(long)-len(short)):
            align_scores[tuple(align)] = self.diff_score(align, long)
        return (tuple(long),) + min(align_scores.items(),key=lambda x: x[1])

    def rhyme_score(self):
        '''returns a tuple containg the lowest-scoring alignment of the lowest-scoring pronuncation combination for the two given words
        and the associated rhyme score'''
        if None in self.prons:
            return (tuple(), tuple(), 666)
        rhyme_pairs = [(self.get_rhyme(v1),self.get_rhyme(v2)) for v1 in self.prons[0] for v2 in self.prons[1]]
        for pair in rhyme_pairs:
            self.possible_prons.append(self.align_score(pair[0],pair[1]))
        best_pair = min(self.possible_prons,key=lambda x: x[2])
        return best_pair

    def get_score(self):
        '''returns the raw score as an int. 
        for futureproofing in case future versions don't calculate score on init'''
        return self.score

    def differing_features(self, group = "none"):
        '''returns a list containing all features that differ between each two rhyme segments
        set group = "cv" to preserve feature changes for consonants and vowels separately (returns a dict)'''
        seg_pairs = [pair for pair in zip(self.best_pair[0],self.best_pair[1]) if None not in pair and self.diff_score([pair[0]],[pair[1]]) > 0]
        if group == "cv":
            diff_features = defaultdict(list)
            for comp in seg_pairs:
                pair_diff = RhymeComp.feature_table.loc[RhymeComp.arpa_dict[comp[0][:2]]].compare(RhymeComp.feature_table.loc[RhymeComp.arpa_dict[comp[1][:2]]]).index.tolist()
                if self.vowel.match(comp[0]) or self.vowel.match(comp[1]):
                    diff_features['V'].extend(pair_diff)
                else:
                    diff_features['C'].extend(pair_diff)
        else:
            diff_features = []
            for comp in seg_pairs:
                diff_features.extend(RhymeComp.feature_table.loc[RhymeComp.arpa_dict[comp[0][:2]]].compare(RhymeComp.feature_table.loc[RhymeComp.arpa_dict[comp[1][:2]]]).index.tolist())
        return diff_features

    def print_segment_scores(self):
        '''prints a table showing a segment-by-segment comparison of the two rhymes'''
        print("Segment Comparisons\n---")
        for comp in zip(self.best_pair[0],self.best_pair[1]):
            print(f'{comp[0]}\t{comp[1]}\t{self.diff_score([comp[0]],[comp[1]])}')

    def print_feature_scores(self):
        '''prints the specific features that differ on each non-identical segment pair'''
        comparisons = []
        seg_pairs = [pair for pair in zip(self.best_pair[0],self.best_pair[1]) if None not in pair and self.diff_score([pair[0]],[pair[1]]) > 0]
        for comp in seg_pairs:
            comparison = RhymeComp.feature_table.loc[RhymeComp.arpa_dict[comp[0][:2]]].compare(RhymeComp.feature_table.loc[RhymeComp.arpa_dict[comp[1][:2]]])
            comparison.rename(columns={'self': comp[0][:2], 'other': comp[1][:2]}, inplace=True)
            comparisons.append(comparison)
        if len(comparisons) > 0:
            print("\nFeature Comparisons\n---")
            for c in comparisons:
                print(c)
    
    def print_all_pronunciations(self):
        '''prints the other possible pronunciations for the words given'''
        if len(self.possible_prons) == 1:
            print('\nNo alternate pronunciations found.')
        else:
            print('\nPossible Pronunciation Comparison:')
            print('---')
            for pair in self.possible_prons:
                print(f'{pair[0]}\t{pair[1]}\t{pair[2]}')

    def print_details(self, verbose=0):
        '''a single print method based on a given integer level for verbose'''
        print(f"'{self.raw_pair[0]}' vs. '{self.raw_pair[1]}'\t SCORE: {self.score}")
        if verbose >= 1:
            self.print_segment_scores()
        if verbose >= 2:
            self.print_feature_scores()
        if verbose >= 3:
            self.print_all_pronunciations()
