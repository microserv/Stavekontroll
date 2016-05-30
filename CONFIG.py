import comm

#Communicationhost, can be used to retrieve IP-addresses og other hosts (services)
comm_host = "http://127.0.0.1:9001"

SPELL_SERVER_PORT = 8002

ALLOWED_ORIGINS = [
    'https://gallifrey.sklirg.io',
    'https://despina.128.no',
]

index_host = 'http://{}:{}/'.format(comm.get_service_ip('index', comm_host), 8001)

#index_host = "http://127.0.0.1:8001/"

try:
    from local_config import *
except ImportError:
    print('Local settings file not found.')
