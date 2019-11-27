from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
import requests

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
        for i in range(N):
            log.append(self.db[-1-i])
        return log

db = Logs("MyLib")


@app.route('/logs')
def showLogs():
    db.showLogs
    pass
    

@app.route('/logs/<int:number>')
def showNLogs(number):
    logs = db.showNLogs(number)
    pass
    

@app.route('/logs',methods=['POST','PUT'])
def AddLog():
    if request.is_json():
        db.add(request.json['data'])
        resp = jsonify("Success")
        resp.status_code = 200
    else:
        resp = jsonify("Unsuccess")
        resp.status_code = 400
    return resp
        
    

def format_message(old,type,date):
    new = {}
    new["name"] = "Logs"
    new["info"] = {}
    for key in old:
        if date != None and date != key["day"]:
            continue
        new["info"][key["day"]]={}
        for element in key['meal']:
            if type != None and type.capitalize() != element['type']:
                continue
            new["info"][key["day"]][element['type']] = []
            for element1 in element['info']:
                new["info"][key['day']][element['type']].append(element1['name']) # Também posso pôr em lista
    return new

def format_date(numero):
    ano = numero%10000
    mes = int((numero%1000000 - numero%10000)/10000)
    dia = int((numero-numero%1000000)/1000000)
    return "%d/%d/%d"%(dia,mes,ano)

if __name__ == '__main__':
    # app.run()
    # app.run(debug=True)
    cfg = config.Canteen()
    app.run(debug=True, host=cfg.host, port=cfg.port)
