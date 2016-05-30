from urlparse import urljoin
import logging
import requests

def get_service_ip(service, comm_host):
    """Using the requests module, sends a get request to 
       the provided communications host for the provided service
       Returns an IP-address of the given service"""
    logger = logging.getLogger(__name__)
    try:
        r = requests.get(urljoin(comm_host, service))
        return r.json()
    except requests.ConnectionError:
        logger.critical('Could not connect to communication-backend to retrieve URI for %s.' % service)
        return None
