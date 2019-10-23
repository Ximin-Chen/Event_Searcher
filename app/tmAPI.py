# import socket
# import sys
import requests
import urllib.request
# import requests_oauthlib
import json

HOST = "https://app.ticketmaster.com"
PATH = "/discovery/v2/events.json"
DEFAULT_KEYWORD = "event"
DEFAULT_RADIUS = 50
API_KEY = "ekOl1mWCrvka6hMLAxMbRnhHHGbNFFEy"

# import ticketpy
#
# client = ticketpy.ApiClient(API_KEY)
# resp = client.venues.find().one()
#
# for venue in resp:
#     print(venue.id)
#     print(venue.name)
#     print(venue.url)
#     # print(venue.distance)
#     print(venue.address+venue.city)
#     print(venue.images[0].get("url"))
url = HOST + PATH + "?apikey="+API_KEY
with urllib.request.urlopen(url) as file:
    page = file.read()
    data = json.loads(page.decode('utf8'))

    print(type(file))
    print(type(page))
    print(data)

def searchItem(lat, lon, keyword):
    if not keyword:
        keyword = DEFAULT_KEYWORD
        






