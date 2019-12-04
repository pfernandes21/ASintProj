from flask import Flask, flash
from flask import render_template
from flask import request, session, abort, redirect, url_for
from flask import jsonify
import requests
import os
import pickle

from datetime import date

import sys
sys.path.append(".")
import config

app = Flask(__name__)

def configFileInit():
    try:
        f = open('ConfigFile', 'rb')
        table = pickle.load(f)
        f.close()
    except IOError:
        table = config.dictMicroservices()
        f = open('ConfigFile', 'wb')
        pickle.dump(table, f)
        f.close()
    print("ConfigInit")
    print(table)
    return table

tableOfMicroservices = configFileInit()

@app.before_request
def log():
    data = {}
    log = {}
    uri = "%s/logs"%(tableOfMicroservices['Log'])
    log['dia'] = date.today().strftime("%d/%m/%Y")
    log['info'] = ('Server %s %s')%(request.method, request.url)
    data['data'] = log
    r = requests.post(uri, json=data)
    print("Register a log was a " + r.text)

@app.before_request
def checkLogging():
    path_split = request.path.split('/')
    if path_split[1] == 'admin' and request.path != '/admin/login':
        if not session.get('logged_in'):
            return render_template("login.html")
        

##################HTML/API###############################
@app.route('/API/<microservice>/<path:path>')
def microservices_API(microservice, path):
    
    try:
        URL = tableOfMicroservices[microservice]
        r = requests.get(URL + "/" + path)
    except KeyError:
        resp = jsonify("Not Found")
        resp.status_code = 404
    except:
        resp = jsonify("Unsuccess")
        resp.status_code = 400
    
    if(r is not None and r.status_code == 200):
        resp = jsonify(r.json())
        resp.status_code = 200
    else:
        resp = jsonify("Unsuccess")
        resp.status_code = 400 

    return resp

##################ADMIN/LOG################################
@app.route('/admin')
def admin_main():
    return render_template('mainadmin.html')

@app.route('/admin/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == 'admin' and request.form['username'] == 'admin':
        session['logged_in'] = True
    else:
        flash('wrong password!')
    return redirect(url_for('admin_main'))

@app.route("/admin/showLogs", methods=['POST','GET'])
def showLogs():
    uri = "%s/logs"%(tableOfMicroservices['Log'])
    try:
        url = ("%s/%s")%(uri,str(request.form['numberOfLogs']))
    except:
        url = uri
    print(url)
    r = requests.get(url)
    if r.status_code != 200:
        return redirect(url_for('admin_main'))
    return render_template("logsTemplate.html", logs=r.json())

@app.route("/admin/queryLogs")
def queryLogs():
    return render_template("logsQuery.html")

@app.route("/admin/changeService")
def changeService():
    try:
        obj = request.args['message']
        print(obj)
    except:
        obj = None

    url = "%s/services"%(tableOfMicroservices['Services'])
    r = requests.get(url)
    if r.status_code != 200:
        return redirect(url_for('admin_main'))
    return render_template("changeShowService.html", service = r.json(), obj = obj)

@app.route("/admin/changeService/<id>")
def changeServiceQuery(id):
    return render_template("serviceQuery.html", ID = id, change = True, obj = None)

@app.route("/admin/deleteService/<id>")
def deleteService(id):
    url = "%s/service/%s"%(tableOfMicroservices['Services'],id)
    r = requests.delete(url)

    if r.status_code == 200:
        return redirect(url_for('changeService',message = "Success"))
    else:
        return redirect(url_for('changeService',message = "Failed"))

@app.route("/admin/changeService/<id>", methods=['POST'])
def changeServicePost(id):
    data = {}
    data['key'] = []
    data['value'] = []
    try:
        if request.form['location'] != '':
            data['key'].append('location')
            data['value'].append(request.form['location'])

        if request.form['name'] != '':
            data['key'].append('name')
            data['value'].append(request.form['name'])

        if request.form['description'] != '':
            data['key'].append('description')
            data['value'].append(request.form['description'])

        if request.form['openTime'] != '':
            data['key'].append('openTime')
            data['value'].append(request.form['openTime'])
    except:
        return redirect(url_for('changeService',message = "Failed"))

    url = "%s/service/%s"%(tableOfMicroservices['Services'],id)
    r = requests.put(url,json=data)

    if r.status_code == 200:
        return redirect(url_for('changeService',message = "Success"))
    else:
        return redirect(url_for('changeService',message = "Failed"))

@app.route("/admin/createService")
def createService():
    return render_template("serviceQuery.html", change=False)

@app.route("/admin/addService", methods=['POST'])
def addService():
    data = {}
    url = "%s/service"%(tableOfMicroservices['Services'])
    allInfo = 0
    try:
        if request.form['location'] != '':
            allInfo += 1
            data['location'] = request.form['location']

        if request.form['name'] != '':
            allInfo += 1
            data['name'] = request.form['name']

        if request.form['description'] != '':
            allInfo += 1
            data['description'] = request.form['description']

        if request.form['openTime'] != '':
            allInfo += 1
            data['openTime'] = request.form['openTime']
    except:
        return render_template("serviceQuery.html", obj = "Failed", change = False, ID = None)
    
    if allInfo != 4:
        return render_template("serviceQuery.html", obj = "Failed", change = False, ID = None)
    
    r = requests.post(url, json=data)
    
    if r.status_code == 200:
        return render_template("serviceQuery.html", obj = "Success", change = False, ID = None)
    else:
        return render_template("serviceQuery.html", obj = "Failed", change = False, ID = None)

@app.route("/admin/configFile")
def configFile():
    try:
        obj = request.args['message']
        print(obj)
    except:
        obj = None

    return render_template("changeConfigFile.html", file = tableOfMicroservices, obj = obj)

@app.route("/admin/changeMicroservice/<key>", methods=['POST'])
def changeMicroservice(key):
    global tableOfMicroservices
    print("Change %s key %s"%(request.form['url'],key))
    try:
        if request.form['url'] != '':
            tableOfMicroservices[key] = request.form['url']
            f = open('ConfigFile', 'wb')
            pickle.dump(tableOfMicroservices, f)
            f.close()
    except:
        return redirect(url_for('configFile', message = "Failed"))

    return redirect(url_for('configFile', message = "Success"))

@app.route("/admin/deleteMicroservice/<key>")
def deleteMicroservice(key):
    global tableOfMicroservices
    try:
        del tableOfMicroservices[key]
        f = open('ConfigFile', 'wb')
        pickle.dump(tableOfMicroservices, f)
        f.close()
    except:
        return redirect(url_for('configFile', message = "Failed"))

    return redirect(url_for('configFile', message = "Success"))

@app.route("/admin/addMicroservice", methods=['POST'])
def addMicroservice():
    global tableOfMicroservices
    try:
        if request.form['name'] != '' and request.form['url'] != '':
            tableOfMicroservices[request.form['name']] = request.form['url']
            f = open('ConfigFile', 'wb')
            pickle.dump(tableOfMicroservices, f)
            f.close()
    except:
        return redirect(url_for('configFile', message = "Failed"))

    return redirect(url_for('configFile', message = "Success"))



if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    # app.run()
    # app.run(debug=True)
    cfg = config.Backend()
    app.run(debug=True, host=cfg.host, port=cfg.port)
