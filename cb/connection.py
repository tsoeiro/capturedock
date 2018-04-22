'''
Connecting to site
'''
from config import *
from time import sleep
import requests
from MyAdapter import MyAdapter

class ClientFactory(object):
    client = None

    def get_client(self):
        if self.client is None:
            self.client = self.create_client()
        return self.client

    def create_client(self):
        logging.info('Connecting to ' + URL)
        client = requests.session()
        client.mount('https://', MyAdapter())
        return client

def Connection(client_factory):
    # Connecting to server
    client = client_factory.get_client()
    count = 0
    while True:
        try:
            # Retrieve the CSRF token first
            r1 = client.get(URL)
            break
        except Exception as e:
            logging.error('Some error during connecting to ' + URL)
            logging.error(e)
            logging.error('Trying again after 60 seconds')
            count += 1
            if count > 5:
                logging.error('Performing delay for 1800 seconds')
                sleep(1800)
                count = 0
            sleep(60)

    if USER in r1.text:
        logging.info('ALREADY LOGGED IN!')
    else:
        logging.info('NOT LOGGED IN!')
        csrftoken = r1.cookies['csrftoken']
        # Set login data and perform submit
        login_data = dict(username=USER, password=PASS, csrfmiddlewaretoken=csrftoken, next='/')
        try:
            r = client.post(URL, data=login_data, headers=dict(Referer=URL))
            page_source = 'Page Source for ' + URL + '\n' + r.text
            if 'You have logged in too many times' in r.text:
                raise Exception('Too many logins deteced')
            # if Debugging is enabled Page source goes to debug.log file
            if Debugging is True:
                Store_Debug(page_source, "connection.log")
        except Exception as e:
            logging.error('Some error during posting to ' + URL)
            logging.error(e)
    return client
