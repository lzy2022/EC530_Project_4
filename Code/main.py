from re import A
from flask_restful import Api, Resource, reqparse
from flask import Flask, url_for, jsonify, request
from celery import Celery
import json
import random
import time
from google.cloud import tasks_v2, speech, storage
from googleapiclient import discovery
from collections import defaultdict
import base64

app = Flask(__name__)
api = Api(app)


client = tasks_v2.CloudTasksClient()

project = 'ec530pj4'
queue = 'V2T'
location = 'us-east4'

parent = client.queue_path(project, location, queue)

task = {
        'app_engine_http_request': {  # Specify the type of request.
            'http_method': tasks_v2.HttpMethod.POST,
            'relative_uri': '/example_task_handler',
            'body': ''
        }
}

task_results = []
task_states = []
for i in range(20):
    task_states.append(0)
    task_results.append('Default MSG')

def get_free_worker():
    for i in range(20):
        if task_states[i] == 0:
            return i


@app.route('/example_task_handler/<int:t_id>', methods=['POST'])
def example_task_handler(t_id):
    # Instantiates a client
    speech_client = speech.SpeechClient()

    # The name of the audio file to transcribe
    payload = request.get_data()
    content = payload
    #gcs_uri = "gs://cloud-samples-data/speech/brooklyn_bridge.raw"
    task_results[t_id] = 'Task Loading...'
    audio = speech.RecognitionAudio(content=content)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    # Detects speech in the audio file
    response = speech_client.recognize(config=config, audio=audio)

    for result in response.results:
        task_results[t_id] = result.alternatives[0].transcript
    task_states[t_id] = 2
    return 'Printed task payload:',201


pars_task_id = reqparse.RequestParser()
pars_task_id.add_argument("task_id", type=int, help="Need task ID", required=True)
class Speech2Text(Resource):
    def post(self, task_id):
        task["app_engine_http_request"]["headers"] = {"Content-type": "application/json"}
        s_file = request.files['file']
        content = s_file.read()
        t_id = get_free_worker()
        task_results[t_id] = 'Loading...'
        task['app_engine_http_request']['relative_uri'] = '/example_task_handler/' + str(t_id)
        encoded_payload = content
        task['app_engine_http_request']['body'] = encoded_payload
        response = client.create_task(parent=parent, task=task)
        task_states[t_id] = 1
        
        return {'task_id':t_id}, 201
    
    def get(self, task_id):
        if task_states[task_id] != 2:
            return {'result': 'Loading'}, 205
        else:
            task_states[task_id] = 0
            return {'result': task_results[task_id]}, 202 

class Speech2Text_taskState(Resource):
    def get(self, task_id):
        return {'task_id': task_id, 'task_state': task_states[task_id]}, 202

api.add_resource(Speech2Text, '/test/<int:task_id>')
api.add_resource(Speech2Text_taskState, '/task_state/<int:task_id>')

if __name__ == "__main__":
    app.run(debug=True)