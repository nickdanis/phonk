'''
this script will create the diffs.csv lookup table
each cell is the number of featural differences between the two sounds, based on the feature system of Hayes (2009)
'''

import cmudict
import re
import pandas as pd

cmu = cmudict.dict()

# collect all arpabet symbols in the given dictionary, for inspection
# ignoring stress for now

arpabet = set()

for word, pronlist in cmu.items():
    for pron in pronlist:
        for segment in pron:
            arpabet.add(segment[:2])

# dictionary to convert from ARPAbet to IPA

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


def to_ipa(arpa_word):
    '''
    convert word from ARPABET to IPA
    '''
    ipa_word = []
    for seg in arpa_word:
        ipa_word.append(arpa_dict[re.sub(r"\d","",seg)])
    return ''.join(ipa_word)

# loads the hayes feature system as a dataframe
# fully specifies feature definitions as 1 (+) vs 0 (-/0)

hayes = pd.read_excel('hayes.xlsx',index_col=0)
hayes.replace(r'\+',1,regex=True,inplace=True)
hayes.replace(r'\-',0,regex=True,inplace=True)
hayes.replace(r'0',0,regex=True,inplace=True)

# add diphthong and syllabic r defintions to hayes

# features for diphthong representation based in Gildea & Jurafsky 1996 (a.o.)
hayes['j-offglide'] = 0
hayes['w-offglide'] = 0

for diph in ['aɪ','eɪ','ɔɪ']:
    hayes.loc[diph] = hayes.loc[diph[0]]
    hayes.loc[diph,'j-offglide'] = 1

for diph in ['oʊ','aʊ']:
    hayes.loc[diph] = hayes.loc[diph[0]]
    hayes.loc[diph,'w-offglide'] = 1

# syllabic r
hayes.loc['ɹ̩'] = hayes.loc['ɹ']
hayes.loc['ɹ̩','syllabic'] = 1

# creates a lookup table for all pairwise feature differences for any two segments in the APRAbet given

# for key, value in arpa_dict.items():
#     ipa_to_arpa[value] = key

diffs = pd.DataFrame(index=list(arpabet),columns=list(arpabet))

for seg1 in diffs.columns:
    for seg2 in diffs.columns:
        diffs.loc[seg1,seg2] = len(hayes.loc[arpa_dict[seg1]].compare(hayes.loc[arpa_dict[seg2]]))

# finally, save to csv 
diffs.to_csv('diffs.csv')