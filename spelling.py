import client
import norvig_spellcheck
from twisted.internet.defer import DeferredList
import json

def index_frequencies():
    indexquery = {'Frequencies_tempquery':'abcdefgh'}
    d_request = client.send_query_to_index(indexquery)
    
    return d_request

def index_completion(query):
    indexquery = {'Partial': True, 'Query': query}
    d_request = client.send_query_to_index(indexquery)
    
    return d_request

class Spelling(object):
    '''prepare returns a dictionary with the result of the spellcheck'''
    def __init__(self, d):
        self.type = d['Type']
        self.query = d['Query']
        self.is_search = d['Search']
        
    def get_result(self):
        if self.is_search:
            result = self.search_spell()
        else:
            result = self.generic_spell()
        return result
        
    def generic_spell(self):
        #NOT_IMPLEMENTED
        return self.search_spell()
 
 
    def complete(self, RF):
        result_s = RF[0][1]
        frequency_s = RF[1][1]
        
        result = json.loads(result_s)
        frequency = json.loads(frequency_s)
        L = result['Result']
        print(L)
        print(frequency)
        sorted_results = sorted(L, key=lambda x:frequency.get(x,1), reverse=True)
        
        print(sorted_results)
        return sorted_results
            
        
    def search_spell(self):
        if self.type.lower() == 'completion':
            d_result = index_completion(self.query.lower())
            d_freqs = index_frequencies()
            
            DL = [d_result, d_freqs]
            callbacks = DeferredList(DL)
            callbacks.addCallback(self.complete)

            result = callbacks
            
        elif self.type.lower() == 'correction':
            #get frequency_list
            result = index_frequencies()
             
            #do statistics
            #...
            
            #result
        print(result)   
        return result
        
        
            

