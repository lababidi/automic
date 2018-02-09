"""This is the main flask module that runs automic"""

import os
import json
import time
from shutil import make_archive
from flask import Flask, render_template, redirect, flash, request, session
from flask import send_from_directory, jsonify, json
from pymongo import MongoClient
from bson.objectid import ObjectId
from paths import *
from isobuilder import iso_builder
from forms import INITCFG, BOOTSTRAP, LICENSE, HEAT, ONAPHEAT, DEPLOY


APP = Flask(__name__, static_folder='static')
APP.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

CLIENT = MongoClient(MONGO_CLIENT)
DB = CLIENT.MachineData


@APP.route('/login', methods=['POST', 'GET'])
def do_admin_login():
    """Login page that validates login"""
    if request.form['username'] == LOGIN_USER and request.form['password'] == LOGIN_PASS:
        session['logged_in'] = True
    else:
        flash('Invalid Credentials')
    return template_test()


@APP.route("/logout")
def logout():
    """Logout page"""
    session['logged_in'] = False
    return template_test()


@APP.route("/")
def template_test():
    """return login page if not logged in"""
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('index.html', name=template_test)


@APP.route('/automic', methods=['GET'])
def automic():
    """return main page"""
    return render_template('automicexplosion.html')


@APP.route('/juju', methods=['GET'])
def juju():
    """redirection to JUJU_GUI website"""
    return redirect(JU_JU)


@APP.route('/automicinitcfg', methods=['GET'])
def automicinitcfg():
    """Init-config file"""
    return render_template('automicinit.html')


@APP.route('/ANSIBLE/allowrule', methods=['GET', 'POST'])
def automicansibleallowrule():
    """ansible allow rule page"""
    return render_template(ANSIBLE_ALLOW)


@APP.route('/ANSIBLE/denyrule', methods=['GET', 'POST'])
def automicansibledenyrule():
    """ansible deny rule page"""
    return render_template(ANSIBLE_DENY)


@APP.route('/ANSIBLE/restart', methods=['GET', 'POST'])
def automicansiblerestart():
    """ansible restart page"""
    return render_template(ANSIBLE_RESTART)


@APP.route('/KVM/automicinitcfg', methods=['GET'])
def automicinitcfgkvm():
    """kvm initcfg page"""
    return render_template('/KVM/automicinit.html')


@APP.route('/Openstack/automicinitcfg', methods=['GET'])
def automicinitcfgopenstack():
    """openstack initcfg page"""
    return render_template('automicinit.html')


@APP.route('/ONAP/automicinitcfg', methods=['GET'])
def automicinitcfgopenecomp():
    """ONAP initcfg page"""
    return render_template('/ONAP/automicinit.html')


@APP.route('/ESXi/automicinitcfg', methods=['GET'])
def automicinitcfgesxi():
    """esxi initcfg page"""
    return render_template('/ESXi/automicinit.html')


@APP.route('/ANSIBLE/automicinitcfg', methods=['GET'])
def automicinitcfgansible():
    """ansible landing page"""
    return render_template('/ANSIBLE/automicinit.html')


@APP.route('/azure/automicinitcfg', methods=['GET'])
def automicinitcfgazure():
    """azure landing page"""
    return render_template('automicinit.html')


@APP.route('/AWS/automicinitcfg', methods=['GET'])
def automicinitcfgaws():
    """AWS initcfg page"""
    return render_template('automicinit.html')


@APP.route('/automicinit', methods=['POST'])
def automicinit():
    """initcfg form values"""
    form = INITCFG(request)
    if request.method == 'POST':

        with open(INIT_CFG) as infile, \
                open(INIT_CFG_OUT, 'w') as outfile:
            for line in infile:
                for src, target in form.initi.items():
                    line = line.replace(src, target)
                outfile.write(line)

        return redirect('/automicbootstrap')

    return render_template('automicboot.html')


@APP.route('/ONAP/automicinit', methods=['POST'])
def automicopenecompinit():
    """ONAP initcfg form values"""
    form = INITCFG(request)
    if request.method == 'POST':

        with open(INIT_CFG) as infile, \
                open(INIT_CFG_ONAP_OUT, 'w') as outfile:
            for line in infile:
                for src, target in form.initi.items():
                    line = line.replace(src, target)
                outfile.write(line)

        return redirect('/ONAP/automicbootstrap')

    return render_template('/ONAP/automicboot.html')


@APP.route('/KVM/automicinit', methods=['POST'])
def automicinitkvm():
    """kvm initcfg form values"""
    form = INITCFG(request)

    if request.method == 'POST':

        with open(INIT_CFG) as infile, \
                open(INIT_CFG_KVM_OUT, 'w') as outfile:
            for line in infile:
                for src, target in form.initi.items():
                    line = line.replace(src, target)
                outfile.write(line)

        return redirect('/KVM/automicbootstrap')

    return render_template('/KVM/automicboot.html')


@APP.route('/ESXi/automicinit', methods=['POST'])
def automicinitesxi():
    """esxi initcfg form values"""
    form = INITCFG(request)

    if request.method == 'POST':

        with open(INIT_CFG) as infile, \
                open(INIT_CFG_ESXI_OUT, 'w') as outfile:
            for line in infile:
                for src, target in form.initi.items():
                    line = line.replace(src, target)
                outfile.write(line)

        return redirect('/ESXi/automicbootstrap')

    return render_template('/ESXi/automicboot.html')


@APP.route('/ONAP/automicbootstrap', methods=['GET'])
def automicbootstrapopenecomp():
    """onap bootstrap landing page"""
    return render_template('/ONAP/automicboot.html')


@APP.route('/KVM/automicbootstrap', methods=['GET'])
def automicbootstrapkvm():
    """kvm bootstrap landing page"""
    return render_template('/KVM/automicboot.html')


@APP.route('/ESXi/automicbootstrap', methods=['GET'])
def automicbootstrapesxi():
    """esxi bootstrap landing page"""
    return render_template('/ESXi/automicboot.html')


@APP.route('/automicbootstrap', methods=['GET'])
def automicbootstrap():
    """bootstrap landing page"""
    return render_template('automicboot.html')


@APP.route('/automicboot', methods=['POST'])
def automicboot():
    """bootstrap form values"""
    form = BOOTSTRAP(request)

    if request.method == 'POST':

        with open(BOOTSTRAP_XML) as infile, \
                open(BOOTSTRAP_XML_OUT, 'w') as outfile:
            for line in infile:
                for src, target in form.booti.items():
                    line = line.replace(src, target)
                outfile.write(line)

        return redirect('/automiclicense')
    return render_template('automiclic.html')


@APP.route('/ONAP/automicboot', methods=['POST'])
def automicbootopenecomp():
    """onap bootstrap form values"""
    form = BOOTSTRAP(request)

    if request.method == 'POST':

        with open(BOOTSTRAP_XML) as infile, \
                open(BOOTSTRAP_XML_ONAP_OUT, 'w') as outfile:
            for line in infile:
                for src, target in form.booti.items():
                    line = line.replace(src, target)
                outfile.write(line)

        return redirect('/ONAP/automiclicense')
    return render_template('/ONAP/automiclic.html')


@APP.route('/KVM/automicboot', methods=['POST'])
def automicbootkvm():
    """kvm bootstrap form values"""
    form = BOOTSTRAP(request)

    if request.method == 'POST':

        with open(BOOTSTRAP_XML) as infile, \
                open(BOOTSTRAP_XML_KVM_OUT, 'w') as outfile:
            for line in infile:
                for src, target in form.booti.items():
                    line = line.replace(src, target)
                outfile.write(line)

        return redirect('/KVM/automiclicense')
    return render_template('/KVM/automiclic.html')


@APP.route('/ESXi/automicboot', methods=['POST'])
def automicbootesxi():
    """esxi bootstrap form values"""
    form = BOOTSTRAP(request)

    if request.method == 'POST':

        with open(BOOTSTRAP_XML) as infile, \
                open(BOOTSTRAP_XML_ESXI_OUT, 'w') as outfile:
            for line in infile:
                for src, target in form.booti.items():
                    line = line.replace(src, target)
                outfile.write(line)

        return redirect('/ESXi/automiclicense')
    return render_template('/ESXi/automiclic.html')


@APP.route('/automiclicense', methods=['GET'])
def automiclicense():
    """license landing page"""
    return render_template('automiclic.html')


@APP.route('/ONAP/automiclicense', methods=['GET'])
def automiclicenseopenecomp():
    """onap license landing page"""
    return render_template('/ONAP/automiclic.html')


@APP.route('/KVM/automiclicense', methods=['GET'])
def automiclicensekvm():
    """kvm license landing page"""
    return render_template('/KVM/automiclic.html')


@APP.route('/ESXi/automiclicense', methods=['GET'])
def automiclicenseesxi():
    """esxi license landing page"""
    return render_template('/ESXi/automiclic.html')


@APP.route('/automiclic', methods=['POST'])
def automiclic():
    """license form values"""
    form = LICENSE(request)

    if request.method == 'POST':

        with open(AUTH_CODE, 'w') as ini:
            ini.write(form.li)
            ini.flush()
        return redirect('/automicheattemplate')
    return render_template('automicheat.html')


@APP.route('/ONAP/automiclic', methods=['POST'])
def automiclicopenecomp():
    """onap license form values"""

    form = LICENSE(request)

    if request.method == 'POST':

        with open(AUTH_CODE_ONAP_OUT, 'w') as ini:
            ini.write(form.li)
            ini.flush()
        return redirect('/ONAP/automicheattemplate')
    return render_template('/ONAP/automicheat.html')


@APP.route('/KVM/automiclic', methods=['POST'])
def automiclickvm():
    """kvm license form values"""
    form = LICENSE(request)
    iso = iso_builder
    if request.method == 'POST':

        with open(AUTH_CODE_KVM_OUT, 'w') as ini:
            ini.write(form.li)
            ini.flush()
        iso.iso_builder_kvm()

        time.sleep(3)
        return redirect('/KVM/automicpackage')
    return render_template('/KVM/automicpkg.html')


@APP.route('/ESXi/automiclic', methods=['POST'])
def automiclicesxi():
    """esxi license form value"""
    form = LICENSE(request)
    iso = iso_builder
    if request.method == 'POST':

        with open(AUTH_CODE_ESXI_OUT, 'w') as ini:
            ini.write(form.li)
            ini.flush()
        iso.iso_builder_esxi()

        time.sleep(3)
        return redirect('/ESXi/automicpackage')
    return render_template('/ESXi/automicexplosionpkg.html')


@APP.route('/automicheattemplate', methods=['GET'])
def automicheattemplate():
    """heat template landing page"""
    return render_template('automicexplosionheat.html')


@APP.route('/ONAP/automicheattemplate', methods=['GET'])
def automicheattemplateopenecomp():
    """onap heat template landing page"""
    return render_template('/ONAP/automicexplosionheat.html')


@APP.route('/automicheat', methods=['POST'])
def automicheat():
    """heat template form values"""
    form = HEAT(request)

    if request.method == 'POST':

        with open(HEAT_ENV) as infile, \
                open(HEAT_ENV_OUT, 'w') as outfile:
            for line in infile:
                for src, target in form.heati.items():
                    line = line.replace(src, target)
                outfile.write(line)
        archive_name = \
            os.path.expanduser(os.path.join('~', OPENSTACK_DOWNLOAD))
        root_dir = \
            os.path.expanduser(os.path.join('~', OPENSTACK_ZIP))
        make_archive(archive_name, 'zip', root_dir)

        return redirect('/automicpackage')
    return render_template('automicexplosionpkg.html')


@APP.route('/ONAP/automicheat', methods=['POST'])
def automicheatopenecomp():
    """onap heat template form values"""
    form = ONAPHEAT(request)

    if request.method == 'POST':

        with open(ONAP_ENV) as infile, \
                open(ONAP_ENV_OUT, 'w') as outfile:
            for line in infile:
                for src, target in form.heati.items():
                    line = line.replace(src, target)
                outfile.write(line)
        archive_name = \
            os.path.expanduser(os.path.join('~', ONAP_DOWNLOAD))
        root_dir = \
            os.path.expanduser(os.path.join('~', ONAP_ZIP))
        make_archive(archive_name, 'zip', root_dir)

        return redirect('/ONAP/automicpackage')
    return render_template('/ONAP/automicexplosionpkg.html')


@APP.route('/upload', methods=['POST'])
def upload():
    """upload files"""
    return render_template('automicupload.html')


@APP.route('/automicpackage', methods=['GET'])
def automicpackage():
    """download package"""
    return render_template('automicexplosionpkg.html')


@APP.route('/ONAP/automicpackage', methods=['GET'])
def automicpackageopenecomp():
    """onap download package"""
    return render_template('/ONAP/automicexplosionpkg.html')


@APP.route('/KVM/automicpackage', methods=['GET'])
def automicpackagekvm():
    """KVM download page"""
    return render_template('/KVM/automicexplosionpkg.html')


@APP.route('/ESXi/automicpackage', methods=['GET'])
def automicpackageesxi():
    """esxi download page"""
    return render_template('/ESXi/automicexplosionpkg.html')


@APP.route('/static/bootstrap-archive.zip', methods=['GET', 'POST'])
def download():
    """download link"""
    return send_from_directory(APP.static_folder, filename='bootstrap-archive.zip')


@APP.route('/static/bootstrap-archive-kvm.iso', methods=['GET', 'POST'])
def downloadkvm():
    """kvm download link"""
    return send_from_directory(APP.static_folder, filename='bootstrap-archive-kvm.iso')


@APP.route('/static/bootstrap-archive-esxi.iso', methods=['GET', 'POST'])
def downloadesxi():
    """esxi download link"""
    return send_from_directory(APP.static_folder, filename='bootstrap-archive-esxi.iso')


@APP.route('/ONAP/automicdeploycreds', methods=['GET'])
def automicdeploycreds():
    """deploy landing page"""
    return render_template('/ONAP/automicdeploycreds.html')


@APP.route('/ONAP/automicdeploy', methods=['POST'])
def automicdeploy():
    """deploy form values"""
    form = DEPLOY(request)

    if request.method == 'POST':

        with open(DEPLOY) as infile, \
                open(DEPLOY_SAVE, 'w') as outfile:
            for line in infile:
                for src, target in form.initi.items():
                    line = line.replace(src, target)
                outfile.write(line)

        return redirect('/ONAP/automicdeploy')

    return render_template('/ONAP/automicdeploy.html')


@APP.route("/addmachine", methods=['POST'])
def addmachine():
    """add instance to be deployed"""
    try:
        json_data = request.json['info']
        devicename = json_data['device']
        ipaddress = json_data['ip']
        username = json_data['username']
        password = json_data['password']
        portnumber = json_data['port']

        DB.Machines.insert_one({
            'device': devicename, 'ip': ipaddress, 'username': username,
            'password': password, 'port': portnumber
        })
        return jsonify(status='OK', message='inserted successfully')

    except Exception as e:
        return jsonify(status='ERROR', message=str(e))


@APP.route('/list')
def showmachinelist():
    """show instances"""
    return render_template('lists.html')


@APP.route('/getmachine', methods=['POST'])
def getmachine():
    """get instance details"""
    try:
        machineid = request.json['id']
        machine = DB.Machines.find_one({'_id': ObjectId(machineid)})
        machinedetail = {
            'device': machine['device'],
            'ip': machine['ip'],
            'username': machine['username'],
            'password': machine['password'],
            'port': machine['port'],
            'id': str(machine['_id'])
        }
        return json.dumps(machinedetail)
    except Exception as e:
        return str(e)


@APP.route('/updatemachine', methods=['POST'])
def updatemachine():
    """update instance"""
    try:
        machineinfo = request.json['info']
        machineid = machineinfo['id']
        device = machineinfo['device']
        ip = machineinfo['ip']
        username = machineinfo['username']
        password = machineinfo['password']
        port = machineinfo['port']

        DB.Machines.update_one({'_id': ObjectId(machineid)}, {
            '$set': {'device': device, 'ip': ip, 'username': username,
                     'password': password, 'port': port}})
        return jsonify(status='OK', message='updated successfully')
    except Exception as e:
        return jsonify(status='ERROR', message=str(e))


@APP.route("/getmachinelist", methods=['POST'])
def getmachinelist():
    """get instance list"""
    try:
        machines = DB.Machines.find()

        machinelist = []
        for machine in machines:
            print(machine)
            machineitem = {
                'device': machine['device'],
                'ip': machine['ip'],
                'username': machine['username'],
                'password': machine['password'],
                'port': machine['port'],
                'id': str(machine['_id'])
            }
            machinelist.APP.nd(machineitem)
    except Exception as e:
        return str(e)
    return json.dumps(machinelist)


@APP.route("/execute", methods=['POST'])
def execute():
    """run command on instance"""
    try:
        machineinfo = request.json['info']
        ip = machineinfo['ip']
        username = machineinfo['username']
        password = machineinfo['password']
        command = machineinfo['command']
        isroot = machineinfo['isroot']

        env.host_string = username + '@' + ip
        env.password = password
        resp = ''
        with settings(warn_only=True):
            if isroot:
                resp = sudo(command)
            else:
                resp = run(command)

        return jsonify(status='OK', message=resp)
    except Exception as e:
        print('Error is ' + str(e))
        return jsonify(status='ERROR', message=str(e))


@APP.route("/deletemachine", methods=['POST'])
def deletemachine():
    """remove instance"""
    try:
        machineid = request.json['id']
        DB.Machines.remove({'_id': ObjectId(machineid)})
        return jsonify(status='OK', message='deletion successful')
    except Exception as e:
        return jsonify(status='ERROR', message=str(e))


@APP.route('/connector/nuage/', methods=['GET'])
def automicconnectornuage():
    """Nuage connector landing page"""
    return render_template('/connector/nuage/automicinit.html')


@APP.route('/connector/openstack/', methods=['GET'])
def automicconnectoropenstack():
    """Openstack connector landing page"""
    return render_template('/connector/openstack/automicinit.html')


if __name__ == "__main__":
    APP.secret_key = os.urandom(12)
    APP.run(host=HOST_ADDRESS, port=HOST_PORT, debug=True)
