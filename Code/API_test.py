import requests
import json
import time

BASE = "http://ec530pj4.uk.r.appspot.com/"

response = requests.post(BASE + "test", {'url':'gs://cloud-samples-data/speech/brooklyn_bridge.raw', 'task_id': 6})
print(response.json())
response = requests.get(BASE + "task_state", {'url':'gs://cloud-samples-data/speech/brooklyn_bridge.raw', 'task_id': 1})
print(response.json())
#a = response.json()['testLLLL']
#b = json.loads(a)
#print(b['url'])
    

