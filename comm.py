from urlparse import urljoin
import requests

def get_service_ip(service, comm_host):
    """Using the requests module, sends a get request to 
       the provided communications host for the provided service
       Returns an IP-address of the given service"""
    r = requests.get(urljoin(comm_host, service))
    return r.json()
