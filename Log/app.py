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
    """
    Class that saves the logs of the server of the Project
    """
    def __init__(self, name):
        self.name = name
        try:
            f = open('LogDB'+self.name, 'rb')
            self.db = pickle.load(f)
            f.close()
        except IOError:
            self.db = {}
        self.count = sum([len(self.db[x]) for x in self.db])
        print("There are already %d elements"%(self.count))

    def add(self,log):
        try:
            self.db[log['dia']].append(log['info'])
        except:
            self.db[log['dia']] = []
            self.db[log['dia']].append(log['info'])
        f = open('LogDB'+self.name, 'wb')
        pickle.dump(self.db, f)
        f.close()
        self.count += 1

    def showLogs(self):
        """
        Return all the logs
        """
        return  self.db

    def showNLogs(self,N):
        """
        Return the last N logs
        """
        log = {}
        if self.count > 0:
            if N > self.count:
                return self.db
            i = 0
            keys = list(self.db.keys())
            while i < N:
                for key in reversed(keys):
                    log[key] = []
                    for info in reversed(self.db[key]):
                        log[key].append(info)
                        i += 1
                        if i >= N:
                            return log
        return log

db = Logs("")


@app.route('/logs')
def showLogs():
    """
    Return all the logs that are saved
    """
    try:
        logs = db.showLogs()
        resp = jsonify(logs)
        resp.status_code = 200
    except:
        resp = jsonify("Unsuccess")
        resp.status_code = 400 
    return resp
    

@app.route('/logs/<int:number>')
def showNLogs(number):
    """
    Return the last N logs that were save
    """
    try:
        logs = db.showNLogs(number)
        if logs == []:
            resp = jsonify("Não há Logs")
        else:
            resp = jsonify(logs)
        resp.status_code = 200
    except:
        resp = jsonify("Unsuccess")
        resp.status_code = 400 
    return resp
    
@app.route('/logs',methods=['POST','PUT'])
def AddLog():
    """
    Save a Log that came from a outside request
    """
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
