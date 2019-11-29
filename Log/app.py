from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
import requests
import json

import pickle

from datetime import date

import sys
sys.path.append(".")
import config

app = Flask(__name__)


class Logs:
    def __init__(self, name):
        self.name = name
        try:
            f = open('LogDB'+self.name, 'rb')
            self.db = pickle.load(f)
            f.close()
        except IOError:
            self.db = []

    def add(self,log):
        self.db.append(log)
        f = open('LogDB'+self.name, 'wb')
        pickle.dump(self.db, f)
        f.close()

    def showLogs(self):
        return  self.db

    def showNLogs(self,N):
        log = []
        print(N)
        if len(self.db) > 0:
            if N > len(self.db):
                return self.db
            for i in range(N):
                log.append(self.db[-1-i])
        return log

db = Logs("MyLib")


@app.route('/logs')
def showLogs():
    try:
        logs = db.showLogs()
        resp = jsonify(logs)
        resp.status_code = 200
    except:
        resp = jsonify("Unuccess")
        resp.status_code = 400 
    return resp
    

@app.route('/logs/<int:number>')
def showNLogs(number):
    try:
        logs = db.showNLogs(number)
        if logs == []:
            resp = jsonify("Não há Logs")
        else:
            resp = jsonify(logs)
        resp.status_code = 200
    except:
        resp = jsonify("Unuccess")
        resp.status_code = 400 
    return resp
    
@app.route('/logs',methods=['POST','PUT'])
def AddLog():
    if request.is_json:
        db.add(request.json['data'])
        resp = jsonify("Success")
        resp.status_code = 200
    else:
        resp = jsonify("Unsuccess")
        resp.status_code = 400
    return resp

if __name__ == '__main__':
    # app.run()
    # app.run(debug=True)
    cfg = config.Log()
    app.run(debug=True, host=cfg.host, port=cfg.port)
