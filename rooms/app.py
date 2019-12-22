from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
import requests

import roomsCache

import sys
sys.path.append(".")
import config

from datetime import date

app = Flask(__name__)
db = roomsCache.Cache("")

FenixSpacesAPI_URL = "https://fenix.tecnico.ulisboa.pt/api/fenix/v1/spaces"

Log = config.Log()
uri = "http://%s:%d/logs"%(Log.host,Log.port)

@app.before_request
def log():
    """
    Save the logs on the microservice Log
    """
    data = {}
    log = {}
    log['dia'] = date.today().strftime("%d/%m/%Y")
    log['info'] = ('Rooms IP: %s %s %s')%(request.remote_addr,request.method, request.url)
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
    
@app.route('/building/<int:buildingid>')
def buildings(buildingid):
    """
    Return the rooms of a building
    """
    if db.checkCache(buildingid):
        resp = jsonify(db.showCache(buildingid))
        resp.status_code = 200

    try:
        r = requests.get(FenixSpacesAPI_URL + "/" + str(buildingid))
        data = r.json()

        if(data['type'] != 'BUILDING'):
            resp = jsonify("Not Found")
            resp.status_code = 404
        else:
            list_rooms = {}
            rooms = getRooms(data)
            list_rooms['name'] = 'Building %s'%(data['name'])
            list_rooms['info'] = rooms

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
    """
    Return the info of a room
    """
    if db.checkCache(roomid):
        data = db.showCache(roomid)
        get_events(data["info"],None,None)
        resp = jsonify(data)
        resp.status_code = 200
    else:
        try:
            r = requests.get(FenixSpacesAPI_URL + "/" + str(roomid))
            data = r.json()

            if(data['type'] != 'ROOM'):
                resp = jsonify("Not Found")
                resp.status_code = 404

            else:
                data = format_room(data)
                db.add(roomid, data)
                get_events(data["info"],None,None)
                resp = jsonify(data)
                resp.status_code = 200

        except Exception as e:
            print(e)
            resp = jsonify("Unsuccess")
            resp.status_code = 400

    return resp

@app.route('/room/<int:roomid>/events/<eventtype>')
def room_event_type(roomid, eventtype):
    """
    Return the info of a room with a certain type of event
    """
    if db.checkCache(roomid):
        data = db.showCache(roomid)
        get_events(data["info"],eventtype,None)
        resp = jsonify(data)
        resp.status_code = 200
    else:
        try:
            r = requests.get(FenixSpacesAPI_URL + "/" + str(roomid))
            data = r.json()

            if(data['type'] != 'ROOM'):
                resp = jsonify("Not Found")
                resp.status_code = 404

            else:
                data = format_room(data)
                db.add(roomid, data)
                get_events(data["info"],eventtype,None)
                resp = jsonify(data)
                resp.status_code = 200

        except Exception as e:
            print(e)
            resp = jsonify("Unsuccess")
            resp.status_code = 400

    return resp

@app.route('/room/<int:roomid>/events/date/<path:eventdate>')
def room_event_date(roomid, eventdate):
    """
    Return the info of a room with a certain date of event
    """
    if db.checkCache(roomid):
        data = db.showCache(roomid)
        get_events(data["info"],None,eventdate)
        resp = jsonify(data)
        resp.status_code = 200
    else:
        try:
            r = requests.get(FenixSpacesAPI_URL + "/" + str(roomid))
            data = r.json()

            if(data['type'] != 'ROOM'):
                resp = jsonify("Not Found")
                resp.status_code = 404

            else:
                data = format_room(data)
                db.add(roomid, data)
                get_events(data["info"],None,eventdate)
                resp = jsonify(data)
                resp.status_code = 200

        except Exception as e:
            print(e)
            resp = jsonify("Unsuccess")
            resp.status_code = 400

    return resp

@app.route('/room/<int:roomid>/events/<eventtype>/<path:eventdate>')
def room_event_type_date(roomid, eventtype, eventdate):
    """
    Return the info of a room with a certain type and date of event
    """
    if db.checkCache(roomid):
        data = db.showCache(roomid)
        get_events(data["info"],eventtype,eventdate)
        resp = jsonify(data)
        resp.status_code = 200
    else:
        try:
            r = requests.get(FenixSpacesAPI_URL + "/" + str(roomid))
            data = r.json()

            if(data['type'] != 'ROOM'):
                resp = jsonify("Not Found")
                resp.status_code = 404

            else:
                data = format_room(data)
                db.add(roomid, data)
                get_events(data["info"],eventtype,eventdate)
                resp = jsonify(data)
                resp.status_code = 200

        except Exception as e:
            print(e)
            resp = jsonify("Unsuccess")
            resp.status_code = 400

    return resp

def get_events(room, tipo, date):
    """
    Filter the events of a room
    """
    if(type(tipo) is str):
        tipo = tipo.upper()
    target_events = []
    events = room['events']
    
    for event in events:
        if (tipo == None and date == None):
            target_events.append(format_event(event))
        elif event['type'] == tipo and date == None:
            target_events.append(format_event(event))
        elif tipo == None and event['day'] == date:
            target_events.append(format_event(event))
        elif event['type'] == tipo and event['day'] == date:
            target_events.append(format_event(event))
    
    room['events'] = target_events


def getRooms(building_data):
    """
    Get the rooms from all floors of a building
    """
    rooms = []
    floors = building_data['containedSpaces']
    for floor in floors:
        if(floor['type'] == 'FLOOR'):
            r = requests.get(FenixSpacesAPI_URL + "/" + str(floor['id']))
            floor_data = r.json()
            for floor_rooms in floor_data['containedSpaces']:
                if(floor_rooms['type'] == 'ROOM'):
                    rooms.append(format_floor(floor_rooms))
    return rooms

def format_event(event):
    """
    Filter information of an event
    """
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
    """
    Filter information of a room
    """
    new = {}
    new["name"] = "Room"
    new["info"] = {}
    for key in room:
        if key != "containedSpaces" and key != "topLevelSpace" and key != "parentSpace" and key != 'description' and key != 'id' and key!= 'type':
            new["info"][key] = room[key]
    return new

def format_floor(floor):
    """
    Filter information of a floor
    """
    new = {}
    for key in floor:
        if key != "containedSpaces" and key != "topLevelSpace" and key != "parentSpace" and key != 'type':
            new[key] = floor[key]
    return new

if __name__ == '__main__':
    # app.run()
    # app.run(debug=True)
    cfg = config.Rooms()
    app.run(debug=True, host=cfg.host, port=cfg.port)