from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
import requests

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
#@app.route()


if __name__ == '__main__':
    # app.run()
    # app.run(debug=True)
    cfg = config.Backend()
    app.run(debug=True, host=cfg.host, port=cfg.port)
