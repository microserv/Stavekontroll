import client
import norvig_spellcheck
from twisted.internet.defer import DeferredList
import json
def generate_keytree(freqdict):
    D = {}
    for word in freqdict:
        d = D
        for letter in word:
            letter = letter.lower()
            if letter in d:
                current = d[letter]
                d = current[1]
            else:
                current = [0, {}]
                d[letter] = current
                d = current[1]
        current[0] = 1
    return D
def check_prefix(prefix, keytree):
    D = keytree
    d = D
    L = []
    for (i,letter) in enumerate(prefix,1):
        letter = letter.lower()
        if letter in d:
            ex,d = d[letter]
            #if ex > 0:
            #    L.append(prefix[0:i].lower())
    if ex > 0:
        L.append(prefix.lower())
    def dfs(d,C):
        for key in d:
            C2 = C[:] + [key]
            ex,d2 = d[key]
            if ex > 0:
                L.append(prefix.lower() + ''.join(C2).lower())
            dfs(d2,C2)
    dfs(d,[])
    return L


def index_frequencies():
    indexquery = {'Frequencies_tempquery':'abcdefgh'}
    d_request = client.send_query(indexquery, CONFIG.index_host')
    
    return d_request

def index_completion(query):
    indexquery = {'Partial': True, 'Query': query}
    d_request = client.send_query(indexquery, CONFIG.index_host)
    
    return d_request

class Spelling(object):
    '''prepare returns a dictionary with the result of the spellcheck'''
    def __init__(self, d,server):
        self.type = d['Type']
        self.query = d['Query']
        self.is_search = d['Search']

        self.server = server
        
        self.completion_query_minlen = 3
    def get_frequencies(self):
        return self.server.freqs
        
    def complete(self, result_list,frequency_dict,lim=10):
        L = check_prefix(self.query.lower(), self.server.keytree)
        frequency = frequency_dict
        sorted_results = sorted(L, key=lambda x:frequency.get(x,1), reverse=True)[:10]        
        return sorted_results

    def complete_deferreds(self, RF):
            result_s = RF[0][1]
            frequency_s = RF[1][1]
            
            result = json.loads(result_s)
            frequency_dict = json.loads(frequency_s)
            result_list = result['Result']
            
            return self.complete(result_list, frequency_dict, 10)



    def correct(self, freqs, query):
        suggestions = norvig_spellcheck.correct(query, freqs)
        return suggestions
        
    def spellcheck(self):
        USE_INDEX_FOR_SEARCH = self.is_search

        #do search-specific (using article keywords/frequencies) spellcheck
        if USE_INDEX_FOR_SEARCH:
            d_freqs = index_frequencies()
            if self.type.lower() == 'completion':
                d_result = index_completion(self.query.lower())
                
                callbacks = DeferredList([d_result, d_freqs])
                x = callbacks.addCallback(self.complete_deferreds)
                
                result = callbacks
            elif self.type.lower() == 'correction':
                callbacks = DeferredList([d_freqs])
                callbacks.addCallback(lambda x:self.correct(x,self.query.lower()))

                result = callbacks
        #do generic spellcheck
        else:
            freqs = self.get_frequencies()
            if self.type.lower() == 'completion':
                if len(self.query) <= self.completion_query_minlen:
                    return []
                results = freqs.keys()
                return self.complete(results, freqs, 10)

            elif self.type.lower() == 'correction':
                freqs = self.get_frequencies()
                results = self.correct(freqs, self.query.lower())
                return results
        return result
        
         

