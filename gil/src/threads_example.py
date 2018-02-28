from pprint import pprint
import requests
from threading import Thread
from time import sleep


def get_date_time():
    print('Getting date time from json test site...')
    for x in range(50):
        print('{}th request for date'.format(x))
        requests.get('http://date.jsontest.com')
    pprint('DateTime response: {}'.format(
        requests.get('http://date.jsontest.com')))


def get_headers():
    print('Getting headers from json test site...')
    for x in range(30):
        print('{}th request for headers'.format(x))
        requests.get('http://headers.jsontest.com')
    pprint('Headers response: {}'.format(
        requests.get('http://headers.jsontest.com')))


t1 = Thread(target=get_date_time, daemon=True)
t2 = Thread(target=get_headers, daemon=True)


t1.start()
t2.start()


for x in range(30):
    sleep(.5)
    print(x)


t2.join()
t1.join()
