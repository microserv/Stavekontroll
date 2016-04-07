from twisted.web import server, resource
from twisted.internet import reactor
from twisted.python import log
from twisted.internet.protocol import ClientFactory, Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint,connectProtocol

import json

def send_query_to_index(query):
        indexquery_string = json.dumps(query)
      
        QUERY = """
POST / HTTP/1.1
User-Agent: Spellcheck
Content-Type: application/json
Content-Length: {LEN}

{JSON_STRING}""".strip().replace('\n', '\r\n').format(LEN=len(indexquery_string), 
                                                      JSON_STRING=indexquery_string)
        F = IndexClientFactory(QUERY)
        #F.protocol = IndexClient
        #F.requestquery = QUERY
        point = TCP4ClientEndpoint(reactor, "127.0.0.1", 8001)
        d = point.connect(F)
        d.addCallback(lambda x:F.idata)
        return d
class IndexClientFactory(ClientFactory):
    def __init__(self, QUERY):
        self.idata = ''
        self.protocol = IndexClient
        self.requestquery = QUERY

class IndexClient(Protocol):
    def connectionMade(self):
        self.transport.write(self.factory.requestquery)
    def dataReceived(self, data):
        self.factory.idata += data    
    #def dataReceived(self, data):
    #    stdout.write(data)
