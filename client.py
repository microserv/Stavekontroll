from twisted.internet import reactor
from twisted.python import log
from twisted.internet.protocol import Protocol
from twisted.internet.defer import Deferred

from StringIO import StringIO
from twisted.web.http_headers import Headers
from twisted.web.client import Agent, FileBodyProducer

import json
class BeginningPrinter(Protocol):
    def __init__(self, finished):
        self.finished = finished
        self.remaining = 1024 * 10
        self.data = ''
    def dataReceived(self, bytes):
        if self.remaining:
            display = bytes[:self.remaining]
            self.data += display
            self.remaining -= len(display)

    def connectionLost(self, reason):
        print(self.data)
        print(dir(self.finished))
        self.finished.callback(self.data)

def send_query_to_index(query):
        indexquery_string = json.dumps(query)
      
        QUERY = """
POST / HTTP/1.1
User-Agent: Spellcheck
Content-Type: application/json
Content-Length: {LEN}

{JSON_STRING}""".strip().replace('\n', '\r\n').format(LEN=len(indexquery_string), 
                                                      JSON_STRING=indexquery_string)
        agent = Agent(reactor)
        d = agent.request('POST', 'http://127.0.0.1:8001/',None,FileBodyProducer(StringIO(indexquery_string)))
        def cbRequest(response):
            finished = Deferred()
            response.deliverBody(BeginningPrinter(finished))
            return finished
        d = d.addCallback(cbRequest)
        return d


#curl -i -H "Content-Type: application/json" -X POST -d '{"Type":"completion", "Search":true, "Query":"forskr"}' 127.0.0.1:8050
