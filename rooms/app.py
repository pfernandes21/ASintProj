from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
import requests

import roomsCache

import sys
sys.path.append(".")
import config

app = Flask(__name__)
db = roomsCache.Cache("MyLib")

URI = "https://fenix.tecnico.ulisboa.pt/api/fenix/v1/spaces"

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

# @app.route('/room/<int:roomid>/events/<eventtype>')

# @app.route('/room/<int:roomid>/events/<date:eventdate>')

# @app.route('/room/<int:roomid>/events/<eventtype>/<date:eventdate>')

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
