from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify

app = Flask(__name__)

@app.route('/menus')

@app.route('/menus/type')

@app.route('/menus/<date:menudate>')

@app.route('/menus/type/<date:menudate>')

if __name__ == '__main__':
    # app.run()
    app.run(debug=True)
