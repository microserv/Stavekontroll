from twisted.internet import reactor
from twisted.python import log
from twisted.internet.protocol import Protocol
from twisted.internet.defer import Deferred

from StringIO import StringIO
from twisted.web.http_headers import Headers
from twisted.web.client import Agent, FileBodyProducer

from urlparse import urljoin

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
        self.finished.callback(self.data)


def get_service_host(service, comm_host):
        agent = Agent(reactor)
        d = agent.request('GET', urljoin(comm_host, service),None,None)
        def cbRequest(response):
            finished = Deferred()
            response.deliverBody(BeginningPrinter(finished))
            return finished
        d.addCallback(cbRequest)
        return d

