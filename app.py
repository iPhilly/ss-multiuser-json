hashkey = None
url = None

import os
import sys
from signal import SIGABRT, SIGILL, SIGINT, SIGSEGV, SIGTERM, signal
from hashlib import md5
import urllib3
from flask import Flask, request, abort, json
from shadowsocks_handler.handler import ShadowsocksManager

app = Flask(__name__)
ss = ShadowsocksManager(os.path.realpath('bin/ssserver'), '/tmp/shadowsocks-manager.sock', os.path.realpath('./ss-config.json'))
ss.start_ss()

def auth_check():
    if hashkey == None:
        return None
    hash_str = request.headers.get('SS-Hash')
    origin_string = "{method}:{body}-{key}".format(method=request.method, body=request.data, key=hashkey)
    md5_object = md5()
    md5_object.update(origin_string)
    print md5_object.hexdigest()
    if not (hash_str and hash_str == md5_object.hexdigest()):
        abort(401)
        return 401
    else:
        return None

app.before_request(auth_check)

@app.route('/')
def hello():
    return ss.ping()

@app.route('/', methods=['PUT'])
def add():
    input_data = json.loads(request.data)
    return ss.add(input_data['port'], input_data['password'])

@app.route('/', methods=['DELETE'])
def remove():
    input_data = json.loads(request.data)
    return ss.remove(input_data['port'])

def push_data(data):
    print data
    if not url == None:
        http = urllib3.PoolManager()
        http.request('POST', url, fields={'data': data})
print ss.ping()
ss.start_listen(push_data)

def on_exit(*args):
    print args
    ss.stop_ss()
    sys.exit(0)

for sig in (SIGABRT, SIGILL, SIGINT, SIGSEGV, SIGTERM):
    signal(sig, on_exit)

if __name__ == '__main__':
    app.run('0.0.0.0', 3000)
