#-*- coding:utf8 -*-
from twisted.web import server, resource
from twisted.internet import reactor
from twisted.python import log
from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint

import json
import spelling

    
class SpellServer(resource.Resource):
    isLeaf = True
    def render_POST(self, request):
        request_dict = json.load(request.content)

        result = self.process_query(request_dict)        
        if type(result) == str:
            return result
        else:
            #result.addCallback(lambda x:x.factory.idata)
            result.addCallback(lambda x:x)
            result.addCallbacks(request.write, log.err)
            result.addBoth(lambda x:request.finish())
            return server.NOT_DONE_YET
        
    def process_query(self, request_dict):
        spell = spelling.Spelling(request_dict)
        result = spell.get_result()
        return result

if __name__=='__main__':
    site=server.Site(SpellServer()) 
    reactor.listenTCP(8002,site)
    reactor.run()

