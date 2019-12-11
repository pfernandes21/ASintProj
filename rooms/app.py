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
    
@app.route('/building/<int:buildingid>')
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

        list_rooms = {}
        rooms = getRooms(data)
        list_rooms['name'] = 'Building %s'%(data['name'])
        list_rooms['info'] = rooms

        try:
            db.add(buildingid, list_rooms)
            resp = jsonify(list_rooms)
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

    get_events(data,None,None)
        
    try:
        resp = jsonify(format_room(data))
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

    get_events(data, eventtype, None)

    try:
        resp = jsonify(data)
        resp.status_code = 200
    except Exception as e:
        print(e)
        resp = jsonify("Unsuccess")
        resp.status_code = 400

    return resp

@app.route('/room/<int:roomid>/events/<eventdate>')
def room_event_date(roomid, eventdate):
    r = requests.get(URI + "/" + str(roomid))
    data = r.json()

    if(data['type'] != 'ROOM'):
        resp = jsonify("Not Found")
        resp.status_code = 404
        return resp

    get_events(data, None, eventdate)

    try:
        resp = jsonify(data)
        resp.status_code = 200
    except Exception as e:
        print(e)
        resp = jsonify("Unsuccess")
        resp.status_code = 400

    return resp

@app.route('/room/<int:roomid>/events/<eventtype>/<eventdate>')
def room_event_type_date(roomid, eventtype, eventdate):
    r = requests.get(URI + "/" + str(roomid))
    data = r.json()

    if(data['type'] != 'ROOM'):
        resp = jsonify("Not Found")
        resp.status_code = 404
        return resp

    get_events(data, eventtype, eventdate)

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
        if(event['type'] == type or event['day'] == date or (type == None and date == None)):
            target_events.append(format_event(event))
    
    room['events'] = target_events


def getRooms(building_data):
    rooms = []
    floors = building_data['containedSpaces']
    for floor in floors:
        if(floor['type'] == 'FLOOR'):
            r = requests.get(URI + "/" + str(floor['id']))
            floor_data = r.json()
            for floor_rooms in floor_data['containedSpaces']:
                if(floor_rooms['type'] == 'ROOM'):
                    rooms.append(format_floor(floor_rooms))
    return rooms

def format_event(event):
    del event['period']
    try:
        name= ""
        for course in event['courses']:
            name = "%s "%(course['name'])
        del event['courses']
        event['courses'] = name
    except:
        pass

    try:
        name= event['course']['name']
        del event['course']
        event['course'] = name
    except:
        pass

    return event

def format_room(room):
    new = {}
    new["name"] = "Room"
    new["info"] = {}
    for key in room:
        if key != "containedSpaces" and key != "topLevelSpace" and key != "parentSpace" and key != 'description' and key != 'id' and key!= 'type':
            new["info"][key] = room[key]
    return new

def format_floor(floor):
    new = {}
    for key in floor:
        if key != "containedSpaces" and key != "topLevelSpace" and key != "parentSpace" and key != 'type':
            new[key] = floor[key]
    return new

if __name__ == '__main__':
    # app.run()
    cfg = config.Rooms()
    app.run(debug=True, host=cfg.host, port=cfg.port)
    # app.run(debug=True)
