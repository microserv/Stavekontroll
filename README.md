# Spell

[![Build Status](https://travis-ci.org/microserv/spell-check.svg?branch=master)](https://travis-ci.org/microserv/spell-check) [![Coverage Status](https://coveralls.io/repos/github/microserv/spell-check/badge.svg?branch=master)](https://coveralls.io/github/microserv/spell-check?branch=master)

Given a single word and a Type of either correction or completion,
returns a list of spellcheck corrections or spellcheck completions.

(See .yaml for API [TODO])


JSON:
{
  'Type': str
  'Search': bool
  'Query': str
}

Query: A single word to be queried for various possible spellchecks (determined by type)

Type: One of 'completion', 'correction'. 
Completion is used to complete a partial queryword.
Correction is used to correct a complete queryword.
Both return a list of suggestions. 

Search: Boolean to signify whether the word is a searchterm, or a generic word. 
Searchterms are corrected/completed using an index of words that appear in articles.
Generic words are corrected/completed using a generic list of words.
