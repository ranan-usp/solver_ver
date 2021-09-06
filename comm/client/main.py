#!/usr/bin/env python3
"""
This script provides a PYNQ client.
This is intended to run on the client server (PYNQ).
"""

import argparse
import json
import os
import platform
import requests
import sys
import threading
import time
from flask import Flask, render_template, request, g
from urllib.parse import urlparse

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../solver')
import BoardStr
import pynqrouter

app = Flask(__name__)
args = {}
pynq_thread = None
client_baseurl = ""

# Reference: https://teratail.com/questions/52593
class StoppableThread(threading.Thread):
    def __init__(self, target, qname, qstr, qseed):
        super(StoppableThread, self).__init__(target=target)
        self._th_stop = threading.Event()
        self._qname = qname
        self._qstr = qstr
        self._qseed = int(qseed)
        self._answer = None

    def run(self):
        global client_baseurl
        global pynq_thread
        global args

        # Main funciton (the solver should be placed here)
        boardstr = BoardStr.conv_boardstr(self._qstr.split('\n'), 'random', self._qseed)
        result = pynqrouter.solve(boardstr, self._qseed)
        if result['solved']:
            answer = result['solution']
        else:
            answer = None
            pynq_thread = None
            return

        res = {
            "client": client_baseurl,
            "qname": self._qname,
            "answer": answer,
            "cputime": result['elapsed']
        }
        self._answer = answer
        r = requests.post("http://{}/post".format(args["host"]), data=res)

        if args["verbose"]:
            print(res)

        pynq_thread = None

    def stop(self):
        self._th_stop.set()

    def stopped(self):
        return self._th_stop.isSet()

    def get_answer(self):
        return self._answer

@app.route('/start', methods=["POST"])
def start():

    global pynq_thread
    global args
    global client_baseurl

    ans = {"status": "None", "answer": "", "client": client_baseurl}

    if args["verbose"]:
        print(request.form)

    if pynq_thread is None:
        qstr = request.form["question"]
        qname = request.form["qname"]
        qseed = request.form["qseed"]
        pynq_thread = StoppableThread(target=StoppableThread, qname=qname, qstr=qstr, qseed=qseed)

        pynq_thread.start()

        # 実行だけ開始する
        ans["status"] = "Processing"

    else:
        ans = {"status": "Not ready", "answer": ""}

    if args["verbose"]:
        print(ans)

    return json.dumps(ans)

@app.route('/stop')
def stop():

    global pynq_thread

    if pynq_thread is None:
        ans = {"status": "No threads"}
    else:
        pynq_thread.stop()
        ans = {"status": "Stopped"}

    pynq_thread = None

    return json.dumps(ans)

@app.route("/status")
def status():

    global pynq_thread

    res_mes = ""

    if pynq_thread is None:
        res_mes = "Ready"
    else:
        res_mes = "Working"

    res = {"status": res_mes}
    return json.dumps(res)

@app.route("/")
def index():
    return platform.node()

@app.before_request
def before_request():
    global client_baseurl

    _url = request.url
    parse = urlparse(_url)
    client_baseurl = parse.netloc

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="PYNQ client.")
    parser.add_argument("-p", "--port", action="store", type=int, default=5000, help="Port")
    parser.add_argument("-H", "--host", action="store", type=str, default="192.168.4.1:5000", help="Host address")
    parser.add_argument("--debug", action="store_true", default=False, help="Debug mode.")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="Verbose.")
    args = vars(parser.parse_args())

    if args["debug"]:
        app.debug = True
    app.run(host='0.0.0.0', port=args["port"], threaded=True)
