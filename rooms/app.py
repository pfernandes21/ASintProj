from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify

import sys
sys.path.append(".")
import config

app = Flask(__name__)

# @app.route('/building/<int:buildingid>')

# @app.route('/building/<int:buildingid>/rooms')

# @app.route('/room/<int:roomid>')

# @app.route('/room/<int:roomid>/events/<eventtype>')

# @app.route('/room/<int:roomid>/events/<date:eventdate>')

# @app.route('/room/<int:roomid>/events/<eventtype>/<date:eventdate>')

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
    app.run(debug=True)
