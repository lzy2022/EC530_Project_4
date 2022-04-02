import requests
import json
import time
import sys

#BASE = "http://127.0.0.1:5000/"
BASE = "http://ec530pj4.uk.r.appspot.com/"

with open('./This_is_a_test.wav', 'rb') as s_file: 
    response = requests.post(BASE + "test/" + '0', files={'file': s_file})
print(response.json())
t_id = response.json()['task_id']

while True:
    response = requests.get(BASE + "task_state/" + str(t_id))
    state = response.json()['task_state']
    if state == 2:
        break
    time.sleep(0.5)

response = requests.get(BASE + "test/" + str(t_id))
print(response.json())

    

