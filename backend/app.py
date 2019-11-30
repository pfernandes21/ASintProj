from flask import Flask, flash
from flask import render_template
from flask import request, session, abort, redirect, url_for
from flask import jsonify
import requests
import os

from datetime import date

import sys
sys.path.append(".")
import config

app = Flask(__name__)

Log = config.Log()
uri = "http://%s:%d/logs"%(Log.host,Log.port)

Service = config.Services()
uriService = "http://%s:%d"%(Service.host,Service.port)

@app.before_request
def log():
    data = {}
    log = {}
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
@app.route('/API/<path:path>')
def get_dir(path):
    return path

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
    url = "%s/services"%(uriService)
    r = requests.get(url)
    if r.status_code != 200:
        return redirect(url_for('admin_main'))
    return render_template("changeShowService.html", service = r.json())

@app.route("/admin/createService")
def createService():
    return render_template("serviceQuery.html")

@app.route("/admin/addService", methods=['POST'])
def addService():
    data = {}
    url = "%s/service"%(uriService)
    try:
        data['location'] = request.form['location']
        data['name'] = request.form['name']
        data['description'] = request.form['description']
        data['openTime'] = request.form['openTime']
        r = requests.post(url, json=data)
    except:
        return render_template("serviceQuery.html", obj = "Failed")
    
    if r.status_code == 200:
        return render_template("serviceQuery.html", obj = "Success")
    else:
        return render_template("serviceQuery.html", obj = "Failed")

@app.route("/admin/configFile")
def configFile():
    return render_template("serviceQuery.html")



if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    # app.run()
    # app.run(debug=True)
    cfg = config.Backend()
    app.run(debug=True, host=cfg.host, port=cfg.port)
