from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
import DBService
import sys
sys.path.append(".")
import config

app = Flask(__name__)
db = DBService.DBService("MyLib")

# @app.errorhandler(404)
# def not_found(error=None):
#     message = {
#             'status': 404,
#             'message': 'Not Found: ' + request.url,
#     }
#     resp = jsonify(message)
#     resp.status_code = 404

#     return resp

@app.route('/services')
def APIListServices():
    try:
        services = db.listAllServices()
    except:
        resp = jsonify("Unsuccess")
        resp.status_code = 404
        return resp

    if services == None:
        resp = jsonify("None")
    else:
        resp = jsonify(services)
        
    resp.status_code = 200
    return resp

@app.route('/service/<serviceid>')
def APIShowService(serviceid):
    try:
        service = db.showService(serviceid)
    except:
        resp = jsonify("Not Found")
        resp.status_code = 400
        return resp
    resp = jsonify(format_message(service.__dict__))
    resp.status_code = 200
    return resp

@app.route('/service', methods=['POST'])
def APICreateService():
    if request.is_json:
        try:
            print(request.json)
            db.addService(request.json['location'],request.json['name'],request.json['description'],request.json['open time'])
        except:
            resp = jsonify("Unsuccess")
            resp.status_code = 400
            return resp
        resp = jsonify("Success")
        resp.status_code = 200
        return resp
    resp = jsonify("No JSON")
    resp.status_code = 400
    return resp

@app.route('/service/<serviceid>', methods=['DELETE'])
def APIDeleteService(serviceid):
    try:
        db.rmService(serviceid)
    except:
        resp = jsonify("Unsuccess")
        resp.status_code = 400
        return resp
    resp = jsonify("Success")
    resp.status_code = 200
    return resp

@app.route('/service/<serviceid>', methods=['PUT'])
def APIChangeService(serviceid):
    if request.is_json:
        print(request.json)
        flag = db.changeService(serviceid,request.json['key'],request.json['value'])
        if flag == "Wrong ID":
            resp = jsonify("Wrong ID")
            resp.status_code = 400
        elif flag == "Wrong Json":
            resp = jsonify("JSON format Wrong")
            resp.status_code = 400
        else:    
            resp = jsonify("Success")
            resp.status_code = 200
        return resp
    resp = jsonify("No JSON")
    resp.status_code = 400
    return resp

def format_message(old):
    new = {}
    new["type"] = {}
    for key in old:
        if key.lower() == "name":
            new[key] = old[key]
            continue
        if key.lower() != "id":
            new["type"][key] = old[key]
    return new



if __name__ == '__main__':
    # app.run()
    cfg = config.Services()
    app.run(debug=True, host=cfg.host, port=cfg.port)
