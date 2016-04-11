#-*- coding:utf8 -*-
from twisted.web import server, resource
from twisted.internet import reactor
#from twisted.python import log
from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint

import json
import spelling
from os import path
class SpellServer(resource.Resource):
    isLeaf = True
    def __init__(self,freqs,keytree):
        self.freqs = freqs
        #self.keytree = spelling.generate_keytree(freqs)
        self.keytree = keytree
        
    def render_POST(self, request):
        request_dict = json.load(request.content)
        print(request_dict)
        result = self.process_query(request_dict)        
        
        #result.addCallback(lambda x:request.write(fx(x)))
        #
        if type(result) == list:
            request.write(json.dumps(result))
            request.finish()
        else:
            result.addCallback(lambda x:request.write(json.dumps(x)))
            result.addCallback(lambda x:request.finish())      
        return server.NOT_DONE_YET
        
    def process_query(self, request_dict):
        spell = spelling.Spelling(request_dict,self)
        result = spell.spellcheck()
        return result

def _generate_frequencies(src_path, dst_path):
    with open(path.join('corpus', '1gram_nob_f1_freq.frk')) as f:
        s = f.read()
    lines = s.decode('latin1').split('\n')
    lines = [x.lstrip().split(' ',1) for x in lines if x.strip()]
    symbols = set('<>.,- _:;!?"\'/&')
    
    LIM = 20
    freqs = {word:int(freq) for freq,word in lines if int(freq) > LIM and not set(word)&symbols}
    '''
    freqs = {}
    for x in lines:
        try: 
            freqs[x[1]] = int(x[0])
        except:
            print(x)
    '''     
    with open(path.join('corpus', 'frequencies_buffered.json'), 'w') as f:
        json.dump(freqs, f)    
    return freqs

def load_frequencies():
    src = path.join('corpus', '1gram_nob_f1_freq.frk')
    dst = path.join('corpus', 'frequencies_buffered.json')
    if not path.exists(dst):
        print("Generating frequencylist for first time launch")
        print("...")
        freqs = _generate_frequencies(src, dst)
    else: 
        print("Loading existing frequencylist...")
        print("(delete {dst} to regenerate at next launch)".format(dst=dst  ))
        with open(dst) as f:
            freqs = json.load(f)
    print("Done")
    return freqs
def load_keytree(freqs):
    dst = path.join('corpus', 'keytree.json')
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
    
    site=server.Site(SpellServer(freqs,keytree)) 
    reactor.listenTCP(8002,site)
    reactor.run()
#freqs = load_frequencies()
#keytree = spelling.generate_keytree(freqs)

