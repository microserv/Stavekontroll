from urlparse import urljoin
import requests

def get_service_ip(service, comm_host):
    r = requests.get(urljoin(comm_host, service))
    return r.json()
