# phonk: some helpful phonetics and phonology functions

Pronounced [fʌŋk], [fɑŋk], [fɔŋk], or even [foʊŋk].

## Installation

Run the following:

```
pip install phonk
```

## Usage

### RhymeComp

So far, the only module is `rhymescore`, which contains the `RhymeComp` class. This is a tool for finding and investigating (poetic) rhymes. Import the `RhymeComp` class directly.

```python
from phonk.rhymescore import RhymeComp

RhymeComp('lives','read').get_score()
```

The `get_score()` method returns a non-negative integer. `0` indicates the rhymes are identical. Any positive number is the number of featural changes between the two rhymes. (See below for exact calculation method.)

To see verbose output (that explains the exact featural differences), use the `print_details()` method. This method takes an integer argument (default is `verbose=1`); the higher the number, the more detail shown.

```python
RhymeComp('lives','read').print_details()
```

The above will output the following:

```
'lives' vs. 'read'       SCORE: 10
Segment Comparisons
---
IH1     EH1     1
V       None    6
Z       D       3

Feature Comparisons
---
       IH   EH
high  1.0  0.0
                   Z    D
continuant       1.0  0.0
delayed release  1.0  0.0
strident         1.0  0.0

Possible Pronunciation Comparison:
---
('IH1', 'V', 'Z')       ('EH1', None, 'D')      10
('IH1', 'V', 'Z')       ('IY1', None, 'D')      10
('AY1', 'V', 'Z')       ('EH1', None, 'D')      12
('AY1', 'V', 'Z')       ('IY1', None, 'D')      14
```

The function has pulled each word from the CMU pronouncing dictionary. Because each word has multiple listed pronunciations, and the rhymes are of different length, the function compares all possible alignments of all possible pronunciations. The best alignment of each pronunciation is printed at the end. The Segment Comparison shows that the lower score occurs when `Z` is compared with `D`. The `V` of `lives` is compared with an empty position. The default score for such a comparison is `6`; this can be changed by setting a value to `e_comp` when creating the object.

The details of each segment-to-segment comparison are shown in the Feature Comparison tables. The feature set is based on [Hayes 2012](https://linguistics.ucla.edu/people/hayes/IP/#features). This is a relatively standard set of features; definitions for which can be found in chapter 4 of the aforementioned textbook. To access these features directly, call the `differing_features()` method, which returns them in a list. 

```python
print(RhymeComp('lives','read').differing_features())

>>> ['high', 'continuant', 'delayed release', 'strident']
```

## Under the hood

### Getting pronunciations

The function will load and search the [CMU pronouncing dictionary](http://www.speech.cs.cmu.edu/cgi-bin/cmudict) via [cmudict](https://pypi.org/project/cmudict/) for pronunciations of the given words. As the CMU might not be accurate, the function can also accept an ARPAbet list representation directly.

If there are multiple pronunciations found, the lowest-scoring pronunciation is used for the base calculation. Alternate pronunciations can be viewed via the `print_details(verbose=3)` method, or the `possible_prons` attribute directly. 

### Defining 'rhyme'

By default, the rhyme comparison looks at the last `VC*#` sequence of the two words (i.e. the linguistic rhyme of the final syllable). If you want to compare multiple syllables, set `syllables=n` upon object creation. If a given word is shorter than `n` syllables, the comparison stops at the length of the shortest word. Currently, stress information is ignored for rhyme calculation.

### Aligning rhymes

If two rhymes are of different length, they must be aligned. The shorter of the two rhymes is padded with an empty object (`None`) at every possible position, and each of these sequences is compared with the longer rhyme. The lowest-scoring comparison is used for the eventual result. Any comparison of a segment to an empty position is given an arbitrary score of `6`. This can be changed by setting a different value to `e_comp` upon object creation. 

### Scoring rhymes

The score of the rhyme comparison is the sum of all featural differences between the two segments, in addition to the `e_comp` value for every empty comparison done. In essence, a fairly standard [faithfulness calculation](https://en.wikipedia.org/wiki/Optimality_Theory#Faithfulness_constraints) is done between the two strings. In the `lives` vs `read` example above, the score breakdown is as follows:

```
Segment Comparisons
---
IH1     EH1     1
V       None    6
Z       D       3
```

Since the rhyme for `read` was shorter, it was padded with `None`. The placement of this padding is such that the score is minimized; comparing `Z` with `D` and `V` with `None` results in a lower score than if e.g. `V` is compared with `D` and `Z` with `None`. 

Once there are two given sequences to compare, score lookup is relatively fast. The `diffs.csv` table includes all ARBAbet symbols as rows and columns with the number of featural differences between them as the values. This table is loaded as a `pandas` dataframe and called for every segmental comparison. 

Only the first instance call of `RhymeComp` loads the relevant tables into memory, making subsequent calculations relatively fast. (h/t [Anupam Basu](https://github.com/ABasu))

## Acknowledgements

Special thanks to: [ABasu](https://github.com/ABasu), [jfloewen](https://github.com/jfloewen), [jrladd](https://github.com/jrladd), [knoxdw](https://github.com/knoxdw), [michaelpginn](https://github.com/michaelpginn), [spenteco](https://github.com/spenteco)