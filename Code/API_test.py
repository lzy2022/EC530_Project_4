import requests
import json
import time

BASE = "http://ec530pj4.uk.r.appspot.com/"

response = requests.get(BASE + "test", {'url':'gs://cloud-samples-data/speech/brooklyn_bridge.raw', 'task_id': 9})
print(response.json())
#a = response.json()['testLLLL']
#b = json.loads(a)
#print(b['url'])
    

