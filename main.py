#!/usr/bin/env python
#-*- coding:utf8 -*-
from twisted.web import server, resource
from twisted.internet import reactor
#from twisted.python import log
from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint

from os import path
import json

import spelling
import CONFIG

from twisted.web.static import File

from twisted.web.resource import NoResource

class SpellServer(resource.Resource):
    """Receives and responds to search queries"""
    isLeaf = True
    def __init__(self,freqs,keytree):
        #super(SpellServer, self).__init__()
        #generic frequency dict
        self.freqs = freqs
        #buffered tree of the frequency dict
        self.keytree = keytree

        #specialized frequencies. Fetch every X
        self.keytree_search = None
        self.timestamp = 0
        self.TTL = 60*10 #10 minutes

        #Stopwords for stemming/ignoring

        with open(path.join('nltk_data','corpora','stopwords','norwegian')) as f:
            self.stopwords = {x.strip() for x in f.readlines()}
 
        print("ONLINE")
    def render_GET(self, request):
        if request.uri == '/static/swagger.json':
            with open(path.join('static', 'swagger.json')) as f:
                s = f.read()
            
            return s
        else:
            return NoResource().render(request)

    def render_POST(self, request):
        request_dict = json.load(request.content)
        result = self.process_query(request_dict)        
        
        #Takes care of the case where response is a deferred by 
        #adding callbacks to write the result when the result is ready.
        if type(result) == list:
            request.write(json.dumps(result))
            request.finish()
        else:
            result.addCallback(lambda x:request.write(json.dumps(x)))
            result.addCallback(lambda x:request.finish())      
        return server.NOT_DONE_YET
        
    def process_query(self, request_dict):
        """Send query for processing, i.e to generate a response depending on query parameters"""    
        spell = spelling.Spelling(request_dict,self)
        result = spell.spellcheck()
        return result
        
def _generate_frequencies(src_path, dst_path,CODING='latin1', FRKLIM=50):
    """Given a frequency file and a destination, generate a dict of 
       frequencies and store the buffered version
       
       FRKLIM is the minimum frequencies a word must have to be included. Very list-specific.
       
       Unlike other the other functions, path is here the full path to the files.
       """
    with open(path.join(src_path)) as f:
        s = f.read()
        
    #Ignore lines that contain certain symbols
    lines = s.decode(CODING).split('\n')
    lines = [x.lstrip().split(' ',1) for x in lines if x.strip()]
    symbols = set('<>.,- _:;!?"\'/&')
    
    #Ignore words with frequencies less than this limit. 
    #The list grows quite quickly with limits lower than 20, requiring relatively much memory (500-1000MB~)
    #and quite a few MB storage space the lower the limit is
    LIM = FRKLIM
    freqs = {word:int(freq) for freq,word in lines if int(freq) > LIM and not set(word)&symbols}
   
    with open(dst_path, 'w') as f:
        json.dump(freqs, f)    
    return freqs

def load_frequencies(frk_linelist='1gram_nob_f1_freq.frk', frk_buffered_outfile='frequencies_buffered.json'):
    """Load frequencies. Generate them if a buffered version does not exist.
       All files are located in the 'corpus' directory, do not include 'corpus' in the path
    """
    src = path.join('corpus', frk_linelist)
    dst = path.join('corpus', frk_buffered_outfile)
    if not path.exists(dst):
        print("Generating frequencylist for first time launch")
        print("...")
        freqs = _generate_frequencies(src, dst)
    else: 
        print("Loading existing frequencylist...")
        print("  (delete {dst} to regenerate at next launch)".format(dst=dst  ))
        with open(dst) as f:
            freqs = json.load(f)
    print("Done")
    return freqs
    
def load_keytree(freqs, keytree_outfile='keytree.json'):
    """Load or generate keytree. 
       This speeds up lookups of frequencies by a lot, but also uses quite a bit of memory
       All files are located in the 'corpus' directory, do not include 'corpus' in the path
       """
    
    dst = path.join('corpus', keytree_outfile)
    if not path.exists(dst):
        print('Generating keytree...')
        keytree = spelling.generate_keytree(freqs)
        with open(dst, 'w') as f:
            json.dump(keytree, f)
        print('Done')
    else:
        print("Loading existing keytree...")
        with open(dst) as f:
            keytree = json.load(f)
        print("Done")
    return keytree

if __name__=='__main__':
    freqs = load_frequencies()
    keytree = load_keytree(freqs)
    resource = SpellServer(freqs,keytree)
    #resource.putChild('static', File('static/'))
    site=server.Site(resource) 
    reactor.listenTCP(CONFIG.SPELL_SERVER_PORT,site)
    reactor.run()

