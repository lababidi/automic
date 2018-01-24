import os
from flask import Flask, render_template, redirect, flash, url_for, request, session
from flask import send_from_directory, jsonify, json
from shutil import make_archive
import logging
import subprocess
import pdb
import time
from subprocess import call
from werkzeug.utils import secure_filename
from pymongo import MongoClient
import json
from bson.objectid import ObjectId
#from fabric.api import *
from flask_restful import Api, Resource, abort

UPLOAD_FOLDER = '~/automic/content/'

app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

client = MongoClient('0.0.0.0:27017')
db = client.MachineData

@app.route('/login', methods=['POST', 'GET'])
def do_admin_login():
    if request.form['username'] == 'automic' and request.form['password'] == 'amc13123!':
        session['logged_in'] = True
    else:
        flash('Invalid Credentials')
    return template_test()


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return template_test()


@app.route("/")
def template_test():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('index.html', name=template_test)



@app.route('/btstrap', methods=['POST'])
def btstrap():
    if request.method == 'POST':
        data = request.form['mgtip', 'mgtmask', 'mgtgateway', 'e1ip', 'e1zone']
        print(data)
        with open('base/init-cfg.txt', 'w') as ini:
            ini.write(initcfg1)
            ini.flush()
    return btstrap

@app.route('/automic', methods=['GET'])
def automic():
    return render_template('automicexplosion.html')

@app.route('/juju', methods=['GET'])
def juju():
    return redirect('https://54.173.97.99/')

@app.route('/automicinitcfg', methods=['GET'])
def automicinitcfg():
    return render_template('automicinit.html')

@app.route('/ANSIBLE/allowrule', methods=['GET','POST'])
def automicansibleallowrule():
    return render_template('/ANSIBLE/automicallowrule.html')

@app.route('/ANSIBLE/denyrule', methods=['GET','POST'])
def automicansibledenyrule():
    return render_template('/ANSIBLE/automicdenyrule.html')

@app.route('/ANSIBLE/restart', methods=['GET','POST'])
def automicansiblerestart():
    return render_template('/ANSIBLE/automicrestart.html')

#automicexplosioninit files

@app.route('/KVM/automicinitcfg', methods=['GET'])
def automicinitcfgkvm():
    return render_template('/KVM/automicinit.html')

@app.route('/Openstack/automicinitcfg', methods=['GET'])
def automicinitcfgopenstack():
    return render_template('automicinit.html')

@app.route('/ONAP/automicinitcfg', methods=['GET'])
def automicinitcfgopenecomp():
    return render_template('/ONAP/automicinit.html')

@app.route('/ESXi/automicinitcfg', methods=['GET'])
def automicinitcfgesxi():
    return render_template('/ESXi/automicinit.html')

@app.route('/ANSIBLE/automicinitcfg', methods=['GET'])
def automicinitcfgansible():
    return render_template('/ANSIBLE/automicinit.html')

@app.route('/azure/automicinitcfg', methods=['GET'])
def automicinitcfgazure():
    return render_template('automicinit.html')

@app.route('/AWS/automicinitcfg', methods=['GET'])
def automicinitcfgaws():
    return render_template('automicinit.html')

#automicinit files

@app.route('/automicinit', methods=['POST'])
def automicinit():
    initi = request.form.to_dict()
    mgti = request.form["mgtip"]
    mgtm = request.form['mgtmask']
    mgtg = request.form['mgtgateway']
    mgtd = request.form['mgtdns']
    hstnme = request.form['hstnme']
    pno = request.form['pno']
    panokey = request.form['panokey']
    if request.method == 'POST':
        print(initi)
        print(request.form)
        print(mgti)
        print("%s" % mgti)

        with open('base/init-cfg.txt') as infile, open('static/bootstrap/config/init-cfg.txt', 'w') as outfile:
            for line in infile:
                for src, target in initi.items():
                    line = line.replace(src, target)
                outfile.write(line)

        return redirect('/automicbootstrap')

    return render_template('automicboot.html')

@app.route('/ONAP/automicinit', methods=['POST'])
def automicopenecompinit():
    initi = request.form.to_dict()
    mgti = request.form["mgtip"]
    mgtm = request.form['mgtmask']
    mgtg = request.form['mgtgateway']
    mgtd = request.form['mgtdns']
    hstnme = request.form['hstnme']
    pno = request.form['pno']
    panokey = request.form['panokey']
    if request.method == 'POST':
        print(initi)
        print(request.form)
        print(mgti)
        print("%s" % mgti)

        with open('onap/base/init-cfg.txt') as infile, open('static/ONAP/bootstrap/init-cfg.txt', 'w') as outfile:
            for line in infile:
                for src, target in initi.items():
                    line = line.replace(src, target)
                outfile.write(line)

        return redirect('/ONAP/automicbootstrap')

    return render_template('/ONAP/automicboot.html')


@app.route('/KVM/automicinit', methods=['POST'])
def automicinitkvm():
    initi = request.form.to_dict()
    mgti = request.form["mgtip"]
    mgtm = request.form['mgtmask']
    mgtg = request.form['mgtgateway']
    mgtd = request.form['mgtdns']
    hstnme = request.form['hstnme']
    pno = request.form['pno']
    panokey = request.form['panokey']

    if request.method == 'POST':
        print(initi)
        print(request.form)
        print(mgti)
        print("%s" % mgti)

        with open('base/init-cfg.txt') as infile, open('static/KVM/bootstrap/config/init-cfg.txt', 'w') as outfile:
            for line in infile:
                for src, target in initi.items():
                    line = line.replace(src, target)
                outfile.write(line)

        return redirect('/KVM/automicbootstrap')

    return render_template('/KVM/automicboot.html')

@app.route('/ESXi/automicinit', methods=['POST'])
def automicinitesxi():
    initi = request.form.to_dict()
    mgti = request.form["mgtip"]
    mgtm = request.form['mgtmask']
    mgtg = request.form['mgtgateway']
    mgtd = request.form['mgtdns']
    hstnme = request.form['hstnme']
    pno = request.form['pno']
    panokey = request.form['panokey']
    if request.method == 'POST':
        print(initi)
        print(request.form)
        print(mgti)
        print("%s" % mgti)

        with open('base/init-cfg.txt') as infile, open('static/ESXi/bootstrap/config/init-cfg.txt', 'w') as outfile:
            for line in infile:
                for src, target in initi.items():
                    line = line.replace(src, target)
                outfile.write(line)

        return redirect('/ESXi/automicbootstrap')

    return render_template('/ESXi/automicboot.html')


#automic bootstrap

@app.route('/ONAP/automicbootstrap', methods=['GET'])
def automicbootstrapopenecomp():
    return render_template('/ONAP/automicboot.html')

@app.route('/KVM/automicbootstrap', methods=['GET'])
def automicbootstrapkvm():
    return render_template('/KVM/automicboot.html')

@app.route('/ESXi/automicbootstrap', methods=['GET'])
def automicbootstrapesxi():
    return render_template('/ESXi/automicboot.html')

@app.route('/automicbootstrap', methods=['GET'])
def automicbootstrap():
    return render_template('automicboot.html')

@app.route('/automicboot', methods=['POST'])
def automicboot():
    booti = request.form.to_dict()
    e1i = request.form['e1ip']
    e1z = request.form['e1zone']
    e1int = request.form['e1inttype']
    e1p = request.form['e1profile']
    e2i = request.form['e2ip']
    e2z = request.form['e2zone']
    e2int = request.form['e2inttype']
    e2p = request.form['e2profile']
    dfrd = request.form['dfrdest']
    dfri = request.form['dfrint']
    dfrnh = request.form['dfrnh']
    aout = request.form['AllowOut']

    if request.method == 'POST':
        print(booti)
        print(request.form)
        print(e1i)
        print(e1z)
        print("%s" % e1z)

        with open('base/bootstrap1.xml') as infile, open('static/bootstrap/config/bootstrap.xml', 'w') as outfile:
            for line in infile:
                for src, target in booti.items():
                    line = line.replace(src, target)
                outfile.write(line)

        return redirect('/automiclicense')
#    else:
    return render_template('automiclic.html')

@app.route('/ONAP/automicboot', methods=['POST'])
def automicbootopenecomp():
    booti = request.form.to_dict()
    e1i = request.form['e1ip']
    e1z = request.form['e1zone']
    e1int = request.form['e1inttype']
    e1p = request.form['e1profile']
    e2i = request.form['e2ip']
    e2z = request.form['e2zone']
    e2int = request.form['e2inttype']
    e2p = request.form['e2profile']
    dfrd = request.form['dfrdest']
    dfri = request.form['dfrint']
    dfrnh = request.form['dfrnh']
    aout = request.form['AllowOut']

    if request.method == 'POST':
        print(booti)
        print(request.form)
        print(e1i)
        print(e1z)
        print("%s" % e1z)

        with open('onap/base/bootstrap1.xml') as infile, open('static/ONAP/bootstrap/bootstrap.xml', 'w') as outfile:
            for line in infile:
                for src, target in booti.items():
                    line = line.replace(src, target)
                outfile.write(line)

        return redirect('/ONAP/automiclicense')
#    else:
    return render_template('/ONAP/automiclic.html')

@app.route('/KVM/automicboot', methods=['POST'])
def automicbootkvm():
    booti = request.form.to_dict()
    e1i = request.form['e1ip']
    e1z = request.form['e1zone']
    e1int = request.form['e1inttype']
    e1p = request.form['e1profile']
    e2i = request.form['e2ip']
    e2z = request.form['e2zone']
    e2int = request.form['e2inttype']
    e2p = request.form['e2profile']
    dfrd = request.form['dfrdest']
    dfri = request.form['dfrint']
    dfrnh = request.form['dfrnh']
    aout = request.form['AllowOut']

    if request.method == 'POST':
        print(booti)
        print(request.form)
        print(e1i)
        print(e1z)
        print("%s" % e1z)

        with open('base/bootstrap1.xml') as infile, open('static/KVM/bootstrap/config/bootstrap.xml', 'w') as outfile:
            for line in infile:
                for src, target in booti.items():
                    line = line.replace(src, target)
                outfile.write(line)

        return redirect('/KVM/automiclicense')
#    else:
    return render_template('/KVM/automiclic.html')

@app.route('/ESXi/automicboot', methods=['POST'])
def automicbootesxi():
    booti = request.form.to_dict()
    e1i = request.form['e1ip']
    e1z = request.form['e1zone']
    e1int = request.form['e1inttype']
    e1p = request.form['e1profile']
    e2i = request.form['e2ip']
    e2z = request.form['e2zone']
    e2int = request.form['e2inttype']
    e2p = request.form['e2profile']
    dfrd = request.form['dfrdest']
    dfri = request.form['dfrint']
    dfrnh = request.form['dfrnh']
    aout = request.form['AllowOut']

    if request.method == 'POST':
        print(booti)
        print(request.form)
        print(e1i)
        print(e1z)
        print("%s" % e1z)

        with open('base/bootstrap1.xml') as infile, open('static/ESXi/bootstrap/config/bootstrap.xml', 'w') as outfile:
            for line in infile:
                for src, target in booti.items():
                    line = line.replace(src, target)
                outfile.write(line)

        return redirect('/ESXi/automiclicense')
#    else:
    return render_template('/ESXi/automiclic.html')

#Automic license

@app.route('/automiclicense', methods=['GET'])
def automiclicense():
    return render_template('automiclic.html')

@app.route('/ONAP/automiclicense', methods=['GET'])
def automiclicenseopenecomp():
    return render_template('/ONAP/automiclic.html')

@app.route('/KVM/automiclicense', methods=['GET'])
def automiclicensekvm():
    return render_template('/KVM/automiclic.html')

@app.route('/ESXi/automiclicense', methods=['GET'])
def automiclicenseesxi():
    return render_template('/ESXi/automiclic.html')

@app.route('/automiclic', methods=['POST'])
def automiclic():

    li = request.form["lic"]

    if request.method == 'POST':

        print(request.form)
        print(li)
        print("%s" % li)
        with open("static/bootstrap/license/authcodes", 'w') as ini:
            ini.write(li)
            ini.flush()
        return redirect('/automicheattemplate')
#    else:
    return render_template('automicheat.html')

@app.route('/ONAP/automiclic', methods=['POST'])
def automiclicopenecomp():

    li = request.form["lic"]

    if request.method == 'POST':

        print(request.form)
        print(li)
        print("%s" % li)
        with open("static/ONAP/bootstrap/authcodes", 'w') as ini:
            ini.write(li)
            ini.flush()
        return redirect('/ONAP/automicheattemplate')
#    else:
    return render_template('/ONAP/automicheat.html')





@app.route('/KVM/automiclic', methods=['POST'])
def automiclickvm():

    li = request.form["lic"]

    if request.method == 'POST':

        print(request.form)
        print(li)
        print("%s" % li)
        with open("static/KVM/bootstrap/license/authcodes", 'w') as ini:
            ini.write(li)
            ini.flush()

        call(["mkisofs", "-J", "-R", "-v", "-V", "'bootstrap'", "-A", "'bootstrap'", \
        "-ldots", "-l", "-allow-lowercase", "-allow-multidot", "-o", \
        "/home/ubuntu/automic/static/bootstrap-archive-kvm.iso", "./static/KVM/bootstrap"])

        time.sleep(3)
        return redirect('/KVM/automicpackage')
#    else:
    return render_template('/KVM/automicpkg.html')

@app.route('/ESXi/automiclic', methods=['POST'])
def automiclicesxi():

    li = request.form["lic"]

    if request.method == 'POST':

        print(request.form)
        print(li)
        print("%s" % li)
        with open("static/ESXi/bootstrap/license/authcodes", 'w') as ini:
            ini.write(li)
            ini.flush()

        call(["mkisofs", "-J", "-R", "-v", "-V", "'bootstrap'", "-A", "'bootstrap'", \
        "-ldots", "-l", "-allow-lowercase", "-allow-multidot", "-o", \
        "/home/ubuntu/automic/static/bootstrap-archive-esxi.iso", "./static/ESXi/bootstrap"])

        time.sleep(3)
        return redirect('/ESXi/automicpackage')
#    else:
    return render_template('/ESXi/automicexplosionpkg.html')

@app.route('/automicheattemplate', methods=['GET'])
def automicheattemplate():
    return render_template('automicexplosionheat.html')

@app.route('/ONAP/automicheattemplate', methods=['GET'])
def automicheattemplateopenecomp():
    return render_template('/ONAP/automicexplosionheat.html')

#heat template

@app.route('/automicheat', methods=['POST'])
def automicheat():
    heati = request.form.to_dict()
    oi = request.form['oin']
    ofb = request.form['ofl']
    omn = request.form['omnn']
    oms = request.form['omsn']
    omi = request.form['omip']
    osn = request.form['osnn']
    oss = request.form['ossn']
    ooi = request.form['ooip']
    oin = request.form['oisn']
    ois = request.form['oiss']
    oii = request.form['oiip']


    if request.method == 'POST':
        print(heati)
        print(request.form)
        print(oi)
        print(oii)
        print("%s" % omi)

        with open('base/heat-environment1.yaml') as infile, open('static/bootstrap/heat-environment.yaml', 'w') as outfile:
            for line in infile:
                for src, target in heati.items():
                    line = line.replace(src, target)
                outfile.write(line)
        archive_name = os.path.expanduser(os.path.join('~', 'automic/static/bootstrap-archive'))
        root_dir = os.path.expanduser(os.path.join('~', 'automic/static/bootstrap'))
        make_archive(archive_name, 'zip', root_dir)

        return redirect('/automicpackage')
#    else:
    return render_template('automicexplosionpkg.html')

@app.route('/ONAP/automicheat', methods=['POST'])
def automicheatopenecomp():
    heati = request.form.to_dict()
    oi = request.form['oin']
    ofb = request.form['ofl']
    omn = request.form['omnn']
    oms = request.form['omsn']
    omi = request.form['omip']
    osn = request.form['osnn']
    oss = request.form['ossn']
    ooi = request.form['ooip']
    oin = request.form['oisn']
    ois = request.form['oiss']
    oii = request.form['oiip']


    if request.method == 'POST':
        print(heati)
        print(request.form)
        print(oi)
        print(oii)
        print("%s" % omi)

        with open('onap/base/base_environment1.env') as infile, open('static/ONAP/bootstrap/base_environment.env', 'w') as outfile:
            for line in infile:
                for src, target in heati.items():
                    line = line.replace(src, target)
                outfile.write(line)
        archive_name = os.path.expanduser(os.path.join('~', 'automic/static/ONAP/bootstrap-archive'))
        root_dir = os.path.expanduser(os.path.join('~', 'automic/static/ONAP/bootstrap'))
        make_archive(archive_name, 'zip', root_dir)

        return redirect('/ONAP/automicpackage')
#    else:
    return render_template('/ONAP/automicexplosionpkg.html')



##############
#Automic upload content files
##############
@app.route('/upload', methods=['POST'])
def upload():

    return render_template('automicupload.html')
###############
#Automic Bootstrap package
###############

@app.route('/automicpackage', methods=['GET'])
def automicpackage():

    return render_template('automicexplosionpkg.html')

@app.route('/ONAP/automicpackage', methods=['GET'])
def automicpackageopenecomp():

    return render_template('/ONAP/automicexplosionpkg.html')

@app.route('/KVM/automicpackage', methods=['GET'])
def automicpackagekvm():
    return render_template('/KVM/automicexplosionpkg.html')

@app.route('/ESXi/automicpackage', methods=['GET'])
def automicpackageesxi():
    return render_template('/ESXi/automicexplosionpkg.html')

@app.route('/static/bootstrap-archive.zip', methods=['GET', 'POST'])
def download():
    return send_from_directory(app.static_folder, filename='bootstrap-archive.zip')

@app.route('/static/bootstrap-archive-kvm.iso', methods=['GET', 'POST'])
def downloadkvm():
    return send_from_directory(app.static_folder, filename='bootstrap-archive-kvm.iso')

@app.route('/static/bootstrap-archive-esxi.iso', methods=['GET', 'POST'])
def downloadesxi():
    return send_from_directory(app.static_folder, filename='bootstrap-archive-esxi.iso')

#################
#Deploy
################

@app.route('/ONAP/automicdeploycreds', methods=['GET'])
def automicdeploycreds():

    return render_template('/ONAP/automicdeploycreds.html')

@app.route('/ONAP/automicdeploy', methods=['POST'])
def automicdeploy():
    initi = request.form.to_dict()
    authurl = request.form["authurl"]
    usr = request.form['usr']
    tenantnme = request.form['tenantnme']
    ospasswd = request.form['ospasswd']
    hstnme = request.form['hstnme']
    cntl1 = request.form['cntl1']
    
    if request.method == 'POST':
        print(initi)
        print(request.form)
        print(mgti)
        print("%s" % mgti)

        with open('onap/base/test.txt') as infile, open('static/ONAP/bootstrap/test.txt', 'w') as outfile:
            for line in infile:
                for src, target in initi.items():
                    line = line.replace(src, target)
                outfile.write(line)

        return redirect('/ONAP/automicdeploy')

    return render_template('/ONAP/automicdeploy.html')

#################
@app.route("/addMachine", methods=['POST'])
def addMachine():
    try:
        json_data = request.json['info']
        deviceName = json_data['device']
        ipAddress = json_data['ip']
        userName = json_data['username']
        password = json_data['password']
        portNumber = json_data['port']

        db.Machines.insert_one({
            'device': deviceName, 'ip': ipAddress, 'username': userName, 'password': password, 'port': portNumber
        })
        return jsonify(status='OK', message='inserted successfully')

    except Exception as e:
        return jsonify(status='ERROR', message=str(e))


@app.route('/list')
def showMachineList():
    return render_template('lists.html')


@app.route('/getMachine', methods=['POST'])
def getMachine():
    try:
        machineId = request.json['id']
        machine = db.Machines.find_one({'_id': ObjectId(machineId)})
        machineDetail = {
            'device': machine['device'],
            'ip': machine['ip'],
            'username': machine['username'],
            'password': machine['password'],
            'port': machine['port'],
            'id': str(machine['_id'])
        }
        return json.dumps(machineDetail)
    except Exception as e:
        return str(e)


@app.route('/updateMachine', methods=['POST'])
def updateMachine():
    try:
        machineInfo = request.json['info']
        machineId = machineInfo['id']
        device = machineInfo['device']
        ip = machineInfo['ip']
        username = machineInfo['username']
        password = machineInfo['password']
        port = machineInfo['port']

        db.Machines.update_one({'_id': ObjectId(machineId)}, {
            '$set': {'device': device, 'ip': ip, 'username': username, 'password': password, 'port': port}})
        return jsonify(status='OK', message='updated successfully')
    except Exception as e:
        return jsonify(status='ERROR', message=str(e))


@app.route("/getMachineList", methods=['POST'])
def getMachineList():
    try:
        machines = db.Machines.find()

        machineList = []
        for machine in machines:
            print
            machine
            machineItem = {
                'device': machine['device'],
                'ip': machine['ip'],
                'username': machine['username'],
                'password': machine['password'],
                'port': machine['port'],
                'id': str(machine['_id'])
            }
            machineList.append(machineItem)
    except Exception as e:
        return str(e)
    return json.dumps(machineList)


@app.route("/execute", methods=['POST'])
def execute():
    try:
        machineInfo = request.json['info']
        ip = machineInfo['ip']
        username = machineInfo['username']
        password = machineInfo['password']
        command = machineInfo['command']
        isRoot = machineInfo['isRoot']

        env.host_string = username + '@' + ip
        env.password = password
        resp = ''
        with settings(warn_only=True):
            if isRoot:
                resp = sudo(command)
            else:
                resp = run(command)

        return jsonify(status='OK', message=resp)
    except Exception as e:
        print('Error is ' + str(e))
        return jsonify(status='ERROR', message=str(e))


@app.route("/deleteMachine", methods=['POST'])
def deleteMachine():
    try:
        machineId = request.json['id']
        db.Machines.remove({'_id': ObjectId(machineId)})
        return jsonify(status='OK', message='deletion successful')
    except Exception as e:
        return jsonify(status='ERROR', message=str(e))

#Automic connector
@app.route('/connector/nuage/', methods=['GET'])
def automicconnectornuage():
    return render_template('/connector/nuage/automicinit.html')

@app.route('/connector/openstack/', methods=['GET'])
def automicconnectoropenstack():
    return render_template('/connector/openstack/automicinit.html')

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(host='0.0.0.0', port=9996, debug=True)
