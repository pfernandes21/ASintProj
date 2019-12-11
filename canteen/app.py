from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
import requests
import json

import canteenCache

from datetime import date,datetime

import sys
sys.path.append(".")
import config

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
db = canteenCache.Cache("")
Log = config.Log()
uri = "http://%s:%d/logs"%(Log.host,Log.port)

URI = "https://fenix.tecnico.ulisboa.pt/api/fenix/v1/canteen"

@app.before_request
def log():
    data = {}
    log = {}
    log['dia'] = date.today().strftime("%d/%m/%Y")
    log['info'] = ('Canteen %s %s')%(request.method, request.url)
    data['data'] = log
    r = requests.post(uri, json=data)
    print(r.text)
    


@app.route('/')
def APIMenus():
    if db.checkCache(date.today().strftime("%d/%m/%Y")):
        resp = jsonify(db.showCache())
        resp.status_code = 200
    else:
        r = requests.get(URI)
        data = r.json()
        new = format_message(data,None,None)
        new['info'] = orderTheData(new['info'])
        try:
            db.add(new)
            resp = jsonify(new)
            resp.status_code = 200
        except Exception as e:
            print(e)
            resp = jsonify("Unsuccess")
            resp.status_code = 400
    return resp

@app.route('/type/<type>')
def APIMenusByType(type):
    if type.lower() == "almoco":
        type = "almoço"
    r = requests.get(URI)
    data = r.json()
    try:
        resp = jsonify(format_message(data,type,None))
        resp.status_code = 200
    except Exception as e:
        print(e)
        resp = jsonify("Unsuccess")
        resp.status_code = 400
    return resp

@app.route('/day/<int:menudate>')
def APIMenusByDay(menudate):
    date = format_date(menudate)
    uri = URI + "?day=%s"%(date)
    r = requests.get(uri)
    data = r.json()
    try:
        resp = jsonify(format_message(data,None,date))
        resp.status_code = 200
    except Exception as e:
        print(e)
        resp = jsonify("Unsuccess")
        resp.status_code = 400
    return resp

@app.route('/<type>/<int:menudate>')
def APIMenusByTypeByDay(type,menudate):
    if type.lower() == "almoco":
        type = "almoço"
    date = format_date(menudate)
    uri = URI + "?day=%s"%(date)
    r = requests.get(uri)
    data = r.json()
    try:
        resp = jsonify(format_message(data,type,date))
        resp.status_code = 200
    except Exception as e:
        print(e)
        resp = jsonify("Unsuccess")
        resp.status_code = 400
    return resp

def orderTheData(data):
    date = []
    for key in data:
        date.append(datetime.strptime(str(key),"%d/%m/%Y"))
    print(date)
    newData = {}
    for key in sorted(date):
        stringDate = datetime.strftime(key,"%d/%m/%Y")
        if stringDate[0] == '0':
            stringDate = stringDate[1:]
        newData[stringDate] = data[stringDate]
    print(newData)

    return newData

def format_message(old,tipo,date):
    new = {}
    new["name"] = "Canteen"
    new["info"] = {}
    for key in old:
        if date != None and date != key["day"]:
            continue
        new["info"][key["day"]]={}
        for element in key['meal']:
            if tipo != None and tipo.capitalize() != element['type']:
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
