import requests
import json
import time

BASE = "http://ec530pj4.uk.r.appspot.com/"

with open('./This_is_a_test.m4a', 'rb') as s_file: 
    response = requests.post(BASE + "test", {'task_id': 4}, files={'file': s_file})
print(response.json())

response = requests.get(BASE + "task_state", {'url':'gs://cloud-samples-data/speech/brooklyn_bridge.raw', 'task_id': 9})
print(response.json())
#a = response.json()['testLLLL']
#b = json.loads(a)
#print(b['url'])

    

