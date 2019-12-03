from flask import Flask
from flask import redirect
from collections import Counter
from flask import request
from flask import jsonify

file = open(r"lusiadas.txt", "r", encoding="utf-8-sig")
wordcount = Counter(file.read().split())
app = Flask(__name__)


@app.route('/')
def hello_world():
    return redirect("static/mainPage.xhtml", code=302)

@app.route('/lusiadas_wc')
def lusiadas_wc():
    return str(len(wordcount))

@app.route('/allwords')
def allwords():
    print (request.form)
    return jsonify(list(wordcount.keys()))

@app.route('/autocomplete', methods=['POST'])
def autocomplete():
    if(request.is_json):
        s = request.json["str"]
        print(s)
        nl = list(filter(lambda x: x.startswith(s), wordcount))
        print(nl)
        return jsonify(nl)
    else:
        return "XXXX"


@app.route('/autocomplete-teste', methods=['POST'])
def autocomplete_teste():
    if(request.is_json):
        print (type(request.json))
        return jsonify(request.json)
    else:
        return request.content_type

@app.route('/search', methods=['POST'])
def search():
    if(request.is_json):
        s = request.json["str"]
        print(s)
        nl = list(filter(lambda x: x.startswith(s), wordcount))
        return jsonify(wordcount[s])
    else:
        return "XXXX"


if __name__ == '__main__':
    app.run()
