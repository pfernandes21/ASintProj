from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify

app = Flask(__name__)

@app.route('/services')

@app.route('/service/<int:serviceid>')

@app.route('/service', methods=['POST'])

@app.route('/service/<int:serviceid>', methods=['PUT'])

if __name__ == '__main__':
    # app.run()
    app.run(debug=True)
