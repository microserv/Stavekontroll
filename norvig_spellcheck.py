#visited 20160314
#http://norvig.com/spell-correct.html
#
#http://norvig.com/spell.py
#Copyright 2007 Peter Norvig. 
#Open source code under MIT license: http://www.opensource.org/licenses/mit-license.php

import re, collections

"""
def words(text):
    return re.findall('[a-z]+', text.lower()) 

def train(words):
    model = collections.defaultdict(lambda: 1)
    for f in words:
        model[f] += 1
    return model

NWORDS = train(words(file('big.txt').read()))
"""

alphabet = 'abcdefghijklmnopqrstuvwxyz'

def edits1(word):
   splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
   deletes    = [a + b[1:] for a, b in splits if b]
   transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
   replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
   inserts    = [a + c + b     for a, b in splits for c in alphabet]
   return set(deletes + transposes + replaces + inserts)

def known_edits2(word):
    return set(e2 for e1 in edits1(word) for e2 in edits1(e1) if e2 in NWORDS)

def known(words): return set(w for w in words if w in NWORDS)

def correct(word, NWORDS):
    candidates = known([word]) or known(edits1(word)) or known_edits2(word) or [word]
    return max(candidates, key=NWORDS.get)

