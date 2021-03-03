# Copyright 2021 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
import subprocess
import signal
import sys
import socket

from flask import request, Flask, jsonify
from ..servable import predict, servable_search

app = Flask(__name__)


@app.route('/predict', methods=['POST'])
def predict_server():
    json_data = request.get_json()
    instance = json_data['instance']
    servable_name = json_data['servable_name']

    res = servable_search(servable_name)
    if res['status'] != 0:
        return jsonify(res)
    servable = res['servables'][0]
    res = predict(instance, servable_name, servable['model'])
    return jsonify(res)


@app.route('/servables', methods=['GET'])
def list_servables():
    return jsonify(servable_search())


def run_flask(host='127.0.0.1', port=5000):
    def net_is_used(host='127.0.0.1', port=5000):
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            s.connect(('127.0.0.1', 5000))
            s.shutdown(2)
            print('Using exiting host...')
        except:
            app.run(host=host, port=port)
    
    net_is_used()


def start_server():
    cmd = ['python -c "from tinyms.serving import run_flask; run_flask()"']
    server_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)

    def signal_handler(signal, frame):
        shutdown()    
        sys.exit(0)
    
    for sig in [signal.SIGINT, signal.SIGHUP, signal.SIGTERM]:
        signal.signal(sig, signal_handler)
   

def shutdown():
    server_pid = subprocess.getoutput("netstat -anp | grep 5000 | awk '{printf $7}' | cut -d/ -f1")
    subprocess.run("kill -9 " + str(server_pid), shell=True)
    return 'Server shutting down...'
