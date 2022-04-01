import requests
import json
import time

BASE = "http://ec530pj4.uk.r.appspot.com/"

response = requests.get(BASE + "test", {'url':'gs://ec530pj4sound/New_Test.m4a', 'task_id': 4})
print(response.json())
response = requests.get(BASE + "task_state", {'url':'gs://cloud-samples-data/speech/brooklyn_bridge.raw', 'task_id': 4})
print(response.json())
#a = response.json()['testLLLL']
#b = json.loads(a)
#print(b['url'])

    

