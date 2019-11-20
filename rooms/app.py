from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify

app = Flask(__name__)

@app.route('/building/<int:buildingid>')

@app.route('/building/<int:buildingid>/rooms')

@app.route('/room/<int:roomid>')

@app.route('/room/<int:roomid>/events/<eventtype>')

@app.route('/room/<int:roomid>/events/<date:eventdate>')

@app.route('/room/<int:roomid>/events/<eventtype>/<date:eventdate>')

if __name__ == '__main__':
    # app.run()
    app.run(debug=True)
