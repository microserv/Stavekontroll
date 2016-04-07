# Stavekontroll
Funksjoner for forslag til utfylling og til korrektur


JSON:
{
  'Type': str
  'Search': bool
  'Query': str
}

Query: A single word to be queried for various possible spellchecks (determined by type)

Type: One of `completion', `correction'. 
Completion is used to complete a partial queryword.
Correction is used to correct a complete queryword.
Both return a list of suggestions. 

Search: Boolean to signify whether the word is a searchterm, or a generic word. 
Searchterms are corrected/completed using an index of words that appear in articles.
Generic words are corrected/completed using a generic list of words.


(Only searchterms are being implemented at the moment; generic completion/correction will be mediocre).
