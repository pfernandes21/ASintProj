from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify

app = Flask(__name__)


if __name__ == '__main__':
    # app.run()
    app.run(debug=True)
