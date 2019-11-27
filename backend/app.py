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
