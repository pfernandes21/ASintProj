from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
import DBService
import sys
sys.path.append(".")
import config

app = Flask(__name__)

@app.route('/services')
def APIListServices():
   pass
@app.route('/service/<int:serviceid>')
def APIShowService(serviceid):
    pass

@app.route('/service', methods=['POST'])
def APICreateService():
   pass

@app.route('/service/<int:serviceid>', methods=['PUT'])
def APIChangeService(serviceid):
    pass

if __name__ == '__main__':
    # app.run()
    cfg = config.Services()
    app.run(debug=True, host=cfg.host, port=cfg.port)
