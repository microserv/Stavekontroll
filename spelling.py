import client
import norvig_spellcheck

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
        
    def search_spell(self):
        if self.type.lower() == 'completion':
            result = index_completion(self.query.lower())
            #TODO Filter by frequencies
            
        elif self.type.lower() == 'correction':
            #get frequency_list
            result = index_frequencies()
             
            #do statistics
            #...
            
            #result
        print(result)
        return result
        
        
            

