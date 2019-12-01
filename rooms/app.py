from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
import requests

import roomsCache

import sys
sys.path.append(".")
import config

import requests

from datetime import date

app = Flask(__name__)
db = roomsCache.Cache("")

URI = "https://fenix.tecnico.ulisboa.pt/api/fenix/v1/spaces"

Log = config.Log()
uri = "http://%s:%d/logs"%(Log.host,Log.port)

@app.before_request
def log():
    data = {}
    log = {}
    log['dia'] = date.today().strftime("%d/%m/%Y")
    log['info'] = ('Rooms %s %s')%(request.method, request.url)
    data['data'] = log
    r = requests.post(uri, json=data)
    print(r.text)
@app.route('/building/<int:buildingid>/rooms')
def buildings(buildingid):
    if db.checkCache(buildingid):
        resp = jsonify(db.showCache(buildingid))
        resp.status_code = 200
    else:
        r = requests.get(URI + "/" + str(buildingid))
        data = r.json()

        if(data['type'] != 'BUILDING'):
            resp = jsonify("Not Found")
            resp.status_code = 404
            return resp

        rooms = getRooms(data)

        try:
            db.add(buildingid, rooms)
            resp = jsonify(rooms)
            resp.status_code = 200
        except Exception as e:
            print(e)
            resp = jsonify("Unsuccess")
            resp.status_code = 400
    return resp

@app.route('/room/<int:roomid>')
def room(roomid):
    r = requests.get(URI + "/" + str(roomid))
    data = r.json()

    if(data['type'] != 'ROOM'):
        resp = jsonify("Not Found")
        resp.status_code = 404
        return resp

    try:
        resp = jsonify(format_message(data))
        resp.status_code = 200
    except Exception as e:
        print(e)
        resp = jsonify("Unsuccess")
        resp.status_code = 400

    return resp

@app.route('/room/<int:roomid>/events/<eventtype>')
def room_event_type(roomid, eventtype):
    r = requests.get(URI + "/" + str(roomid))
    data = r.json()

    if(data['type'] != 'ROOM'):
        resp = jsonify("Not Found")
        resp.status_code = 404
        return resp

    data = get_events(data, eventtype, None)

    try:
        resp = jsonify(data)
        resp.status_code = 200
    except Exception as e:
        print(e)
        resp = jsonify("Unsuccess")
        resp.status_code = 400

    return resp

@app.route('/room/<int:roomid>/events/<date:eventdate>')
def room_event_date(roomid, eventdate):
    r = requests.get(URI + "/" + str(roomid))
    data = r.json()

    if(data['type'] != 'ROOM'):
        resp = jsonify("Not Found")
        resp.status_code = 404
        return resp

    data = get_events(data, None, eventdate)

    try:
        resp = jsonify(data)
        resp.status_code = 200
    except Exception as e:
        print(e)
        resp = jsonify("Unsuccess")
        resp.status_code = 400

    return resp

@app.route('/room/<int:roomid>/events/<eventtype>/<date:eventdate>')
def room_event_type_date(roomid, eventtype, eventdate):
    r = requests.get(URI + "/" + str(roomid))
    data = r.json()

    if(data['type'] != 'ROOM'):
        resp = jsonify("Not Found")
        resp.status_code = 404
        return resp

    data = get_events(data, eventtype, eventdate)

    try:
        resp = jsonify(data)
        resp.status_code = 200
    except Exception as e:
        print(e)
        resp = jsonify("Unsuccess")
        resp.status_code = 400

    return resp

def get_events(room, type, date):
    target_events = []
    events = room['events']
    for event in events:
        if(event['type'] == type or event['day'] == date):
            target_events.append(format_message(event))
    
    return target_events

def getRooms(building_data):
    rooms = []
    floors = building_data['containedSpaces']
    for floor in floors:
        if(floor['type'] == 'FLOOR'):
            r = requests.get(URI + "/" + str(floor['id']))
            floor_data = r.json()
            for floor_rooms in floor_data['containedSpaces']:
                if(floor_rooms['type'] == 'ROOM'):
                    rooms.append(format_message(floor_rooms))
    return rooms

def format_message(old):
    new = {}
    new["info"] = {}
    for key in old:
        if key.lower() == "name":
            new[key] = old[key]
            continue
        if key != "containedSpaces" and key != "topLevelSpace" and key != "parentSpace":
            new["info"][key] = old[key]
    return new

if __name__ == '__main__':
    # app.run()
    cfg = config.Rooms()
    app.run(debug=True, host=cfg.host, port=cfg.port)
    # app.run(debug=True)
