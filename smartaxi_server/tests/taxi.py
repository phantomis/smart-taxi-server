import time
import sys

server = 'http://192.168.0.103:8080/'
location_url = 'api/v1/location/?format=json'
users = [
    {
        "name" : "johndoe",
        "api_key" : "b0d0e53a64b5ad7c358a2dc89a56175b26464682",
        "step" : -0.001
    },
    {
        "name" : "jperez",
        "api_key" : "05af03a5e80fa04cbe920990498496d68537e19c",
        "step" : 0.002
    },
    {
        "name" : "rar",
        "api_key" : "f8d338164f7529cb2eb0bde38afdeee537a29e12",
        "step" : -0.005
    },
]

user = users[int(sys.argv[1])]
print user
url = server + location_url

initial_lat = -33.046104
initial_lng = -71.39073689999998

import httplib2, json


h = httplib2.Http(".cache") # WAT?

while True:

    initial_lat += user["step"]
    initial_lng += user["step"]
    data = {"latitude":str(initial_lat) , "longitude" : str(initial_lng) , "speed" : "30"}
    headers = {"Authorization" : "ApiKey %s:%s" % (user["name"],user["api_key"]) , 'content-type':'application/json'}
    #print data
    #print headers
    resp, content = h.request(url, "POST", json.dumps(data), headers)

    print resp
    print content
    time.sleep(5)