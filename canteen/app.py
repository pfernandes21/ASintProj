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
    """
    Save the logs on the microservice Log
    """
    data = {}
    log = {}
    log['dia'] = date.today().strftime("%d/%m/%Y")
    log['info'] = ('Canteen IP: %s %s %s')%(request.remote_addr,request.method, request.url)
    data['data'] = log
    try:
        r = requests.post(uri, json=data)
    except requests.exceptions.RequestException as e:
        print(e)
        print("\n\nThe microservice Log is unvailable. The Log is %s."%(log['info']))
    else:
        if r.status_code == 200:
            print("Register Log was a success")
        else:
            print("Register Log was an unsuccess")
    


@app.route('/')
def APIMenus():
    """
    Return all the menus of a week
    """
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

@app.route('/type/<tipo>')
def APIMenusByType(tipo):
    """
    Return all one menu of a day during a week (dinner or lunch)
    """
    if tipo.lower() == "almoco":
        tipo = "almoço"
    if db.checkCache(date.today().strftime("%d/%m/%Y")):
        resp = jsonify(db.transform(None,tipo))
        resp.status_code = 200
    else:
        r = requests.get(URI)
        data = r.json()
        try:
            resp = jsonify(format_message(data,tipo,None))
            resp.status_code = 200
        except Exception as e:
            print(e)
            resp = jsonify("Unsuccess")
            resp.status_code = 400
    return resp

@app.route('/day/<path:menudate>')
@app.route('/dia/<path:menudate>')
def APIMenusByDay(menudate):
    """
    Return the menu of a day
    """
    if db.checkCache(menudate):
        resp = jsonify(db.transform(menudate,None))
        resp.status_code = 200
    else:
        uri = URI + "?day=%s"%(menudate)
        r = requests.get(uri)
        data = r.json()
        try:
            resp = jsonify(format_message(data,None,menudate))
            resp.status_code = 200
        except Exception as e:
            print(e)
            resp = jsonify("Unsuccess")
            resp.status_code = 400
    return resp

@app.route('/<tipo>/<path:menudate>')
def APIMenusByTypeByDay(tipo,menudate):
    """
    Return one menu of a day ( lunch or dinner )
    """
    if tipo.lower() == "almoco":
        tipo = "almoço"
    if db.checkCache(menudate):
        resp = jsonify(db.transform(menudate,tipo))
        resp.status_code = 200
    else:
        uri = URI + "?day=%s"%(menudate)
        r = requests.get(uri)
        data = r.json()
        try:
            resp = jsonify(format_message(data,tipo,menudate))
            resp.status_code = 200
        except Exception as e:
            print(e)
            resp = jsonify("Unsuccess")
            resp.status_code = 400
    return resp

def orderTheData(data):
    """
    Order the dict by keys
    """
    date = []
    for key in data:
        date.append(datetime.strptime(str(key),"%d/%m/%Y"))
    newData = {}
    for key in sorted(date):
        stringDate = datetime.strftime(key,"%d/%m/%Y")
        if stringDate[0] == '0':
            stringDate = stringDate[1:]
        newData[stringDate] = data[stringDate]

    return newData

def format_message(old,tipo,date):
    """
    Format the message to send
    """
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
    """
    Format the number to convert to a date format
    """
    ano = numero%10000
    mes = int((numero%1000000 - numero%10000)/10000)
    dia = int((numero-numero%1000000)/1000000)
    return "%d/%d/%d"%(dia,mes,ano)

if __name__ == '__main__':
    # app.run()
    # app.run(debug=True)
    cfg = config.Canteen()
    app.run(debug=True, host=cfg.host, port=cfg.port)
