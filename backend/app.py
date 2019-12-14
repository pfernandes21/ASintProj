from flask import Flask, flash
from flask import render_template
from flask import request, session, abort, redirect, url_for
from flask import jsonify, Markup
import requests
import os
import pickle

from datetime import date

import sys
sys.path.append(".")
import config

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

def configFileInit():
    try:
        f = open('ConfigFile', 'rb')
        table = pickle.load(f)
        f.close()
    except IOError:
        table = config.dictMicroservices()
        f = open('ConfigFile', 'wb')
        pickle.dump(table, f)
        f.close()
    print("ConfigInit")
    print(table)
    return table

tableOfMicroservices = configFileInit()

API_url = 'http://127.0.0.1:5000'

@app.before_request
def log():
    """
    Save the logs on the microservice Log
    """
    data = {}
    log = {}
    uri = "%s/logs"%(tableOfMicroservices['Log'])
    log['dia'] = date.today().strftime("%d/%m/%Y")
    log['info'] = ('Server %s %s')%(request.method, request.url)
    data['data'] = log
    try:
        r = requests.post(uri, json=data)
    except requests.exceptions.RequestException as e:
        print(e)
        print("\n\nThe microservice Log is unvailable. The Log is %s."%(log['info']))
    else:
        if r.status_code == 200:
            print("Register Log was a success")
        else:
            print("Register Log was an unsuccess")

@app.before_request
def checkLogging():
    """
    Check if the admin pages are logged
    """
    path_split = request.path.split('/')
    if path_split[1] == 'admin' and request.path != '/admin/login':
        if not session.get('admin_logged_in'):
            return render_template("login.html")


@app.route("/")
def main():
    return render_template("Main.html")

def jsonToHtml(resJson,h):
    """
    Arguments: JSON and the number for the Markup 'h' \n
    Return: String that contains the HTML \n
    Summary: Convert JSON to HTML
    """
    resHtml = ''
    if type(resJson) is dict:
        for key in resJson:
            resHtml += '<h%d>'%(h) +'%s'%(key) + ' : '  + jsonToHtml(resJson[key],h+1) + '</h%d>'%(h)
    elif type(resJson) is list:
        resHtml += '<ul>'
        for element in resJson:
            resHtml += '<li>' + jsonToHtml(element,h) + '</li>'
        resHtml += '</ul>'
    elif type(resJson) is int or type(resJson) is float:
        resHtml = str(resJson)
    elif type(resJson) is str:
        resHtml = resJson
    return resHtml
        

##################HTML/API###############################
##########################As Páginas de HTML são do genero get<NOME DO SERVIÇO>/<Nome Do Serviço>=<ID>#############################
@app.route('/get<NameService>')
@app.route('/get<NameService>/<path:path>')
def htmlPages(NameService,path=None):
    """
    Generate the html page after requesting information according with the route to the API of the server
    """
    if path == None:
        url = 'http://127.0.0.1:5000/API/%s'%(NameService)
    else:
        path = path.split('=')
        if path[1] == 'today':
            path[1] = date.today().strftime("%d%m%Y")
        try:
            url = 'http://127.0.0.1:5000/API/%s/%s/%s'%(NameService,path[0],path[1])
        except:
            url = None
    
    if url != None:
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            resHtml = jsonToHtml(data['info'],2)
            value = Markup(resHtml)
            return render_template("HTMLTemplate.html", html = value, obj=res.json(), url=url)
    
    return render_template("HTMLTemplate.html", obj={"name":NameService,"info":None}, url=url)
    
#FALTA FAZER PARA RECEBER POST PUT DELETE
@app.route('/API/<microservice>', methods=['GET','POST','PUT','DELETE'])
@app.route('/API/<microservice>/<path:path>', methods=['GET','POST','PUT','DELETE'])
def microservices_API(microservice, path=None):
    """
    API of the Server.\n
    It is also a proxy where it forward correctly to the url of the microservice according with the route.
    """

    #Change create or delete entries of the Table that is used to forward to the correct url of the microservice
    if microservice == 'configFile':
        global tableOfMicroservices
        if request.method == 'GET':
            r = jsonify(tableOfMicroservices)
            r.status_code = 200
            return r
        elif request.method == 'PUT' or request.method == 'POST':
            try:
                tableOfMicroservices[request.json['name']] = request.json['url']
                f = open('ConfigFile', 'wb')
                pickle.dump(tableOfMicroservices, f)
                f.close()
                r = jsonify("SUCCESS")
                r.status_code = 200
            except:
                r = jsonify("FAILED")
                r.status_code = 400
            return r
        elif request.method == 'DELETE':
            try:
                del tableOfMicroservices[request.json['key']]
                f = open('ConfigFile', 'wb')
                pickle.dump(tableOfMicroservices, f)
                f.close()
                r = jsonify("SUCCESS")
                r.status_code = 200
            except:
                r = jsonify("FAILED")
                r.status_code = 400
            return r
    r = None

    # Forward the request to the respective url of the microservice
    try:
        URL = tableOfMicroservices[microservice] + '/' + (path if path != None else "")
        if(request.method == 'GET'):
            r = requests.get(URL)

        elif(request.method == 'POST'):
            print(request.get_json())
            r = requests.post(URL, json = request.get_json())

        elif(request.method == 'PUT'):
            r = requests.put(URL, json = request.get_json())

        elif(request.method == 'DELETE'):
            r = requests.delete(URL)

    except KeyError:
        resp = jsonify("Not Found")
        resp.status_code = 404
    except:
        resp = jsonify("Unsuccess")
        resp.status_code = 400
    
    if(r is not None and r.status_code == 200):
        resp = jsonify(r.json())
        resp.status_code = 200
    else:
        resp = jsonify("Unsuccess")
        resp.status_code = 400 

    return resp

##################ADMIN/LOG################################
@app.route('/admin')
def admin_main():
    return render_template('mainadmin.html')

@app.route('/admin/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == 'admin' and request.form['username'] == 'admin':
        session['admin_logged_in'] = True
    else:
        flash('wrong password!')
    return redirect(url_for('admin_main'))

@app.route("/admin/showLogs", methods=['POST','GET'])
def showLogs():
    uri = "%s/API/Log/logs"%(API_url)
    try:
        url = ("%s/%s")%(uri,str(request.form['numberOfLogs']))
    except:
        url = uri
    print(url)
    r = requests.get(url)
    if r.status_code != 200:
        return redirect(url_for('admin_main'))
    return render_template("logsTemplate.html", logs=r.json())

@app.route("/admin/queryLogs")
def queryLogs():
    """
    Ask the admin user if he wants to see all the logs or how many logs he wants to see.
    """
    return render_template("logsQuery.html")

@app.route("/admin/changeSecretariat")
def changeSecretariat():
    """
    Request the API to show all the secretariats that are possible to change.\n
    And shows to the user.
    """
    try:
        obj = request.args['message']
        print(obj)
    except:
        obj = None

    url = "%s/API/secretariats/secretariats"%(API_url)
    r = requests.get(url)
    if r.status_code != 200:
        return redirect(url_for('admin_main'))
    return render_template("changeShowSecretariat.html", secretariat = r.json(), obj = obj)

@app.route("/admin/changeSecretariat/<id>")
def changeSecretariatQuery(id):
    return render_template("secretariatQuery.html", ID = id, change = True, obj = None)

@app.route("/admin/deleteSecretariat/<id>")
def deleteSecretariat(id):
    """
    Request the API to delete a specific secretariat
    """
    url = "%s/API/secretariats/secretariat/%s"%(API_url,id)
    r = requests.delete(url)

    if r.status_code == 200:
        return redirect(url_for('changeSecretariat',message = "Success"))
    else:
        return redirect(url_for('changeSecretariat',message = "Failed"))

@app.route("/admin/changeSecretariat/<id>", methods=['POST'])
def changeSecretariatPost(id):
    """
    Retrieve from the form the fields that the user wants to change on the secretariat and pass the information to the API.
    """
    data = {}
    data['key'] = []
    data['value'] = []
    try:
        if request.form['location'] != '':
            data['key'].append('location')
            data['value'].append(request.form['location'])

        if request.form['name'] != '':
            data['key'].append('name')
            data['value'].append(request.form['name'])

        if request.form['description'] != '':
            data['key'].append('description')
            data['value'].append(request.form['description'])

        if request.form['openTime'] != '':
            data['key'].append('openTime')
            data['value'].append(request.form['openTime'])
    except:
        return redirect(url_for('changeSecretariat',message = "Failed"))

    url = "%s/API/secretariats/secretariat/%s"%(API_url,id)
    r = requests.put(url,json=data)# MUDAR PARA FAZER REQUEST À API

    if r.status_code == 200:
        return redirect(url_for('changeSecretariat',message = "Success"))
    else:
        return redirect(url_for('changeSecretariat',message = "Failed"))

@app.route("/admin/createSecretariat")
def createSecretariat():
    return render_template("secretariatQuery.html", change=False)

@app.route("/admin/addSecretariat", methods=['POST'])
def addSecretariat():
    """
    Retrieve from the form all the information to create a new secretariat and pass the information to the API.
    """
    data = {}
    url = "%s/API/secretariats/secretariat"%(API_url)
    allInfo = 0
    try:
        if request.form['location'] != '':
            allInfo += 1
            data['location'] = request.form['location']

        if request.form['name'] != '':
            allInfo += 1
            data['name'] = request.form['name']

        if request.form['description'] != '':
            allInfo += 1
            data['description'] = request.form['description']

        if request.form['openTime'] != '':
            allInfo += 1
            data['openTime'] = request.form['openTime']
    except:
        return render_template("secretariatQuery.html", obj = "Failed", change = False, ID = None)
    
    if allInfo != 4:
        return render_template("secretariatQuery.html", obj = "Failed", change = False, ID = None)
    
    r = requests.post(url, json=data) # MUDAR PARA FAZER REQUEST À API
    
    if r.status_code == 200:
        return render_template("secretariatQuery.html", obj = "Success", change = False, ID = None)
    else:
        return render_template("secretariatQuery.html", obj = "Failed", change = False, ID = None)

@app.route("/admin/configFile")
def configFile():
    """
    Request to the API all the information about the forwarding table and present this information to the admin user.
    """
    try:
        obj = request.args['message']
        print(obj)
    except:
        obj = None

    url = "%s/API/configFile"%(API_url)

    r = requests.get(url)

    if r.status_code == 200:
        return render_template("changeConfigFile.html", file = r.json(), obj = obj)
    else:
        return render_template(url_for('admin_main'))

@app.route("/admin/changeMicroservice/<key>", methods=['POST'])
def changeMicroservice(key):
    """
    Retrieve the new url from the form to change a specific entry of the forwarding table and pass this information to the API:
    """
    if request.form['url'] != '':
        url = "%s/API/configFile"%(API_url)
        r = requests.put(url, json={'url':"%s"%(request.form['url']),"name":"%s"%(key)} )
        if r.status_code == 200:
            return redirect(url_for('configFile', message = "Success"))
    return redirect(url_for('configFile', message = "Failed"))

@app.route("/admin/deleteMicroservice/<key>")
def deleteMicroservice(key):
    """
    Request the API to delete a specific entry of the forwarding table.
    """
    url = "%s/API/configFile"%(API_url)
    r = requests.delete(url, json={"key":"%s"%(key)} )
    if r.status_code != 200:
        return redirect(url_for('configFile', message = "Failed"))
    return redirect(url_for('configFile', message = "Success"))

@app.route("/admin/addMicroservice", methods=['POST'])
def addMicroservice():
    """
    Retrieve from the form all the information to create a new entry on the forwarding table and pass this information to the API.
    """
    if request.form['name'] != '' and request.form['url'] != '':
        url = "%s/API/configFile"%(API_url)
        r = requests.post(url, json={'name':"%s"%(request.form['name']),'url':"%s"%(request.form['url'])} )
        if r.status_code == 200:
            return redirect(url_for('configFile', message = "Success"))
    return redirect(url_for('configFile', message = "Failed"))

##################APLICAÇÃO MOBILE################################
@app.route("/mobile/qrcode")
def mobileQrCode():
    return render_template("MobileQrCode.html")

@app.route("/mobile/secret")
def mobileUserValidation():
    return render_template("MobileSecret.html")

@app.route("/mobile/showroomsecretariats")
def mobileShowRoomSecretariats():
    return render_template("MobileShowRoomSecretariat.html") 

if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    # app.run()
    # app.run(debug=True)
    cfg = config.Backend()
    app.run(debug= True, host=cfg.host, port=cfg.port)
