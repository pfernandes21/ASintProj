from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
import DBService
import sys
sys.path.append(".")
import config
import requests
from datetime import date

app = Flask(__name__)
db = DBService.DBService("")

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
    log['info'] = ('Services %s %s')%(request.method, request.url)
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
            db.addService(request.json['location'],request.json['name'],request.json['description'],request.json['openTime'])
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
        try:
            for i in range(len(request.json['key'])):
                flag = db.changeService(serviceid,request.json['key'][i],request.json['value'][i])
                if flag == "Wrong ID" or flag == "Wrong Json":
                    break
        except:
            flag = "Wrong Json"
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
    new["info"] = {}
    new["name"] = "Secretariats"
    for key in old:
        if key.lower() != "id":
            new["info"][key] = old[key]
    return new



if __name__ == '__main__':
    # app.run()
    cfg = config.Services()
    app.run(debug=True, host=cfg.host, port=cfg.port)