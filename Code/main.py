from flask_restful import Api, Resource, reqparse
from flask import Flask, url_for, jsonify, request
from celery import Celery
import json
import random
import time
from google.cloud import tasks_v2, speech, storage
from googleapiclient import discovery
from collections import defaultdict

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


@app.route('/example_task_handler', methods=['POST'])
def example_task_handler():
    # Instantiates a client
    client = speech.SpeechClient()

    # The name of the audio file to transcribe
    payload = request.get_data(as_text=True)
    args = json.loads(payload)
    gcs_uri = args['url']
    t_id = args['t_id']
    #gcs_uri = "gs://cloud-samples-data/speech/brooklyn_bridge.raw"

    audio = speech.RecognitionAudio(uri=gcs_uri)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    # Detects speech in the audio file
    response = client.recognize(config=config, audio=audio)

    for result in response.results:
        print("Transcript: {}".format(result.alternatives[0].transcript))
    # task_results[10] = result.alternatives[0].transcript
    task_results[t_id] = result.alternatives[0].transcript
    task_states[t_id] = 2
    return 'Printed task payload:',201


pars_task_id = reqparse.RequestParser()
pars_task_id.add_argument("task_id", type=int, help="Need task ID", required=True)
pars_file_url = reqparse.RequestParser()
pars_file_url.add_argument("url", type=str, help="Need file url", required=True)
class Speech2Text(Resource):
    def post(self):
        task["app_engine_http_request"]["headers"] = {"Content-type": "application/json"}
        args = pars_file_url.parse_args()
        url = args['url']
        t_id = get_free_worker()
        payload = json.dumps({'url': url, 't_id': t_id})
        task_results[t_id] = 'Loading...'
        encoded_payload = payload.encode()
        task['app_engine_http_request']['body'] = encoded_payload
        response = client.create_task(parent=parent, task=task)
        task_states[t_id] = 1
        return {'task_id':t_id}, 201
    
    def get(self):
        args = pars_task_id.parse_args()
        task_states[args['task_id']] = 0
        return {'result': task_results[args['task_id']]}, 202

class Speech2Text_taskState(Resource):
    def get(self):
        args = pars_task_id.parse_args()
        t_id = args['task_id']
        return {'task_id': t_id, 'task_state': task_states[t_id]}, 202

api.add_resource(Speech2Text, '/test')
api.add_resource(Speech2Text_taskState, '/task_state')

if __name__ == "__main__":
    app.run(debug=True)