from flask import Flask, flash
from flask import render_template
from flask import request, session, abort
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

@app.before_request
def log():
    data = {}
    log = {}
    log['dia'] = date.today().strftime("%d/%m/%Y")
    log['info'] = ('Server %s %s')%(request.method, request.url)
    data['data'] = log
    r = requests.post(uri, json=data)
    print(r.text)

##################HTML/API###############################
@app.route('/API/<path:path>')
def get_dir(path):
    return path

##################ADMIN/LOG################################
@app.route('/admin')
def admin_main():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('mainadmin.html')

@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == 'admin' and request.form['username'] == 'admin':
        session['logged_in'] = True
    else:
        flash('wrong password!')
    return admin_main()


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    # app.run()
    # app.run(debug=True)
    cfg = config.Backend()
    app.run(debug=True, host=cfg.host, port=cfg.port)
