"""This is the main flask module that runs automic"""

import os
import json
import time
from shutil import make_archive
from flask import Flask, render_template, redirect, flash, request, session
from flask import send_from_directory, jsonify, json, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
from paths import *
from isobuilder import iso_builder
from forms import INITCFG, BOOTSTRAP, LICENSE, HEAT, ONAPHEAT, DEPLOY



APP = Flask(__name__, static_folder='static')
APP.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['dms'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


APP.config['UPLOAD_FOLDER2'] = UPLOAD_FOLDER2
APP.config['UPLOAD_FOLDER3'] = UPLOAD_FOLDER3
APP.config['UPLOAD_FOLDER4'] = UPLOAD_FOLDER4

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


#@APP.route('/automic', methods=['GET'])
#def automic():
#    """return main page"""
#    return render_template('automicexplosion.html')


@APP.route('/content', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'Content Udpate' not in request.files:
            if 'Software Update' not in request.files:
                flash('No file part')
                return redirect(request.url)
        try:
            file = request.files['Content Update']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(APP.config['UPLOAD_FOLDER'], filename))
                return redirect(url_for('upload_file',
                                        filename=filename))
        except:
            pass
        try:
            file2 = request.files['Software Update']
            if file2.filename == '':
                return redirect(request.url)
            if file2 and allowed_file(file2.filename):
                filename = secure_filename(file2.filename)
                file2.save(os.path.join(APP.config['UPLOAD_FOLDER2'], filename))
                return redirect(url_for('upload_file',
                                        filename=filename))
        except:
            pass
    return render_template('/KVM/package.html')


@APP.route('/vmcontent', methods=['GET', 'POST'])
def upload_filevm():
    if request.method == 'POST':
        if 'Content Update' not in request.files:
            if 'Software Update' not in request.files:
                flash('No file part')
                return redirect(request.url)
        try:
            file3 = request.files['Content Update']
            if file3.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file3 and allowed_file(file3.filename):
                filename = secure_filename(file3.filename)
                file3.save(os.path.join(APP.config['UPLOAD_FOLDER3'], filename))
                return redirect(url_for('upload_filevm',
                                        filename=filename))
        except:
            pass
        try:
            file4 = request.files['Software Update']
            if file4.filename == '':
                return redirect(request.url)
            if file4 and allowed_file(file4.filename):
                filename = secure_filename(file4.filename)
                file4.save(os.path.join(APP.config['UPLOAD_FOLDER4'], filename))
                return redirect(url_for('upload_filevm',
                                        filename=filename))
        except:
            pass
    return render_template('/VMware/package.html')

"""KVM WORKFLOW"""


@APP.route('/KVM/initcfg', methods=['GET'])
def automicinitcfgkvm():
    """kvm initcfg page"""
    return render_template('/KVM/initcfg.html')


@APP.route('/KVM/init', methods=['POST'])
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

        return redirect('/KVM/bootstrap')

    return render_template('/KVM/bootstrap.html')


@APP.route('/KVM/bootstrap', methods=['GET'])
def automicbootstrapkvm():
    """kvm bootstrap landing page"""
    return render_template('/KVM/bootstrap.html')


@APP.route('/KVM/boot', methods=['POST'])
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

        return redirect('/KVM/license')
    return render_template('/KVM/license.html')


@APP.route('/KVM/license', methods=['GET'])
def automiclicensekvm():
    """kvm license landing page"""
    return render_template('/KVM/license.html')


@APP.route('/KVM/lic', methods=['POST'])
def automiclickvm():
    """kvm license form values"""
    form = LICENSE(request)
    iso = iso_builder
    if request.method == 'POST':

        with open(AUTH_CODE_KVM_OUT, 'w') as ini:
            ini.write(form.li)
            ini.flush()
        iso.iso_builder_kvm('sef')

        time.sleep(3)
        return redirect('/KVM/package')
    return render_template('/KVM/package.html')


@APP.route('/static/bootstrap-archive-kvm.iso', methods=['GET', 'POST'])
def downloadkvm():
    """kvm download link"""
    return send_from_directory(APP.static_folder, filename='bootstrap-archive-kvm.iso')


@APP.route('/KVM/package', methods=['GET'])
def automicpackagekvm():
    """KVM download page"""
    return render_template('/KVM/package.html')


@APP.route('/KVM/automicinitcfg', methods=['GET'])
def automicinitcfgopenstack():
    """openstack initcfg page"""
    return render_template('/KVM/automicinit.html')


"""VMWARE workflow"""


@APP.route('/VMware/initcfg', methods=['GET'])
def automicinitcfgesxi():
    """VMware esxi initcfg page"""
    return render_template('/VMware/initcfg.html')


@APP.route('/VMware/init', methods=['POST'])
def automicinitesxi():
    """VMware esxi initcfg form values"""
    form = INITCFG(request)

    if request.method == 'POST':

        with open(INIT_CFG) as infile, \
                open(INIT_CFG_ESXI_OUT, 'w') as outfile:
            for line in infile:
                for src, target in form.initi.items():
                    line = line.replace(src, target)
                outfile.write(line)

        return redirect('/VMware/bootstrap')

    return render_template('/VMware/bootstrap.html')


@APP.route('/VMware/bootstrap', methods=['GET'])
def automicbootstrapesxi():
    """esxi bootstrap landing page"""
    return render_template('/VMware/bootstrap.html')


@APP.route('/VMware/boot', methods=['POST'])
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

        return redirect('/VMware/license')
    return render_template('/VMware/license.html')


@APP.route('/VMware/license', methods=['GET'])
def automiclicenseesxi():
    """esxi license landing page"""
    return render_template('/VMware/license.html')


@APP.route('/VMware/lic', methods=['POST'])
def automiclicesxi():
    """esxi license form value"""
    form = LICENSE(request)
    iso = iso_builder
    if request.method == 'POST':

        with open(AUTH_CODE_ESXI_OUT, 'w') as ini:
            ini.write(form.li)
            ini.flush()
        iso.iso_builder_esxi('self')

        time.sleep(3)
        return redirect('/VMware/package')
    return render_template('/VMware/package.html')


@APP.route('/VMware/package', methods=['GET'])
def automicpackageesxi():
    """esxi download page"""
    return render_template('/VMware/package.html')


@APP.route('/static/bootstrap-archive-esxi.iso', methods=['GET', 'POST'])
def downloadesxi():
    """esxi download link"""
    return send_from_directory(APP.static_folder, filename='bootstrap-archive-esxi.iso')


"""ansible templates"""


@APP.route('/ANSIBLE/automicinitcfg', methods=['GET'])
def automicinitcfgansible():
    """ansible landing page"""
    return render_template('/ANSIBLE/automicinit.html')


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


"""Microsoft AZURE workflow"""


@APP.route('/AZURE/initcfg', methods=['GET'])
def automicinitcfgazure():
    """azure landing page"""
    return render_template('/AZURE/initcfg.html')


"""Google GCP workflow"""


@APP.route('/GCP/initcfg', methods=['GET'])
def automicinitcfggcp():
    """azure landing page"""
    return render_template('/GCP/initcfg.html')


@APP.route('/GCP/init', methods=['POST'])
def automicinitgcp():
    """initcfg form values"""
    form = INITCFG(request)
    if request.method == 'POST':

        with open(INIT_CFG) as infile, \
                open(INIT_CFG_OUT, 'w') as outfile:
            for line in infile:
                for src, target in form.initi.items():
                    line = line.replace(src, target)
                outfile.write(line)

        return redirect('/GCP/bootstrap')

    return render_template('/GCP/bootstrap.html')


@APP.route('/GCP/bootstrap', methods=['GET'])
def automicbootstrapgcp():
    """bootstrap landing page"""
    return render_template('/GCP/bootstrap.html')


@APP.route('/GCP/bootstrap', methods=['POST'])
def automicbootgcp():
    """bootstrap form values"""
    form = BOOTSTRAP(request)

    if request.method == 'POST':

        with open(BOOTSTRAP_XML) as infile, \
                open(BOOTSTRAP_XML_OUT, 'w') as outfile:
            for line in infile:
                for src, target in form.booti.items():
                    line = line.replace(src, target)
                outfile.write(line)

        return redirect('/GCP/license')
    return render_template('/GCP/license.html')


@APP.route('/GCP/license', methods=['GET'])
def automiclicensegcp():
    """license landing page"""
    return render_template('/GCP/license.html')


@APP.route('/GCP/lic', methods=['POST'])
def automiclicGCP():
    """license form values"""
    form = LICENSE(request)

    if request.method == 'POST':

        with open(AUTH_CODE, 'w') as ini:
            ini.write(form.li)
            ini.flush()
        return redirect('/GCP/heattemplate')
    return render_template('/GCP/heat.html')


@APP.route('/GCP/heat', methods=['POST'])
def automicheatgcp():
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

        return redirect('/GCP/package')
    return render_template('/GCP/package.html')


@APP.route('/GCP/heattemplate', methods=['GET'])
def automicheattemplategcp():
    """heat template landing page"""
    return render_template('/GCP/heat.html')


@APP.route('/GCP/package', methods=['GET'])
def automicpackagegcp():
    """download package"""
    return render_template('/GCP/package.html')


@APP.route('/static/bootstrap-archive.zip', methods=['GET', 'POST'])
def downloadgcp():
    """download link"""
    return send_from_directory(APP.static_folder, filename='bootstrap-archive.zip')



"""AWS workflow"""


@APP.route('/AWS/initcfg', methods=['GET'])
def automicinitcfgaws():
    """AWS initcfg page"""
    return render_template('/AWS/initcfg.html')


@APP.route('/AWS/init', methods=['POST'])
def automicinitaws():
    """initcfg form values"""
    form = INITCFG(request)
    if request.method == 'POST':

        with open(INIT_CFG) as infile, \
                open(INIT_CFG_OUT, 'w') as outfile:
            for line in infile:
                for src, target in form.initi.items():
                    line = line.replace(src, target)
                outfile.write(line)

        return redirect('/AWS/bootstrap')

    return render_template('/AWS/bootstrap.html')


@APP.route('/AWS/bootstrap', methods=['GET'])
def automicbootstrapaws():
    """bootstrap landing page"""
    return render_template('AWS/bootstrap.html')


@APP.route('/AWS/bootstrap', methods=['POST'])
def automicbootaws():
    """bootstrap form values"""
    form = BOOTSTRAP(request)

    if request.method == 'POST':

        with open(BOOTSTRAP_XML) as infile, \
                open(BOOTSTRAP_XML_OUT, 'w') as outfile:
            for line in infile:
                for src, target in form.booti.items():
                    line = line.replace(src, target)
                outfile.write(line)

        return redirect('/AWS/license')
    return render_template('/AWS/license.html')


@APP.route('/AWS/license', methods=['GET'])
def automiclicenseaws():
    """license landing page"""
    return render_template('/AWS/license.html')


@APP.route('/AWS/lic', methods=['POST'])
def automiclicaws():
    """license form values"""
    form = LICENSE(request)

    if request.method == 'POST':

        with open(AUTH_CODE, 'w') as ini:
            ini.write(form.li)
            ini.flush()
        return redirect('/AWS/cfttemplate')
    return render_template('/AWS/cloudformationtemplate.html')


@APP.route('/AWS/cloudformationtemplate', methods=['POST'])
def automicheataws():
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

        return redirect('/AWS/package')
    return render_template('AWS/package.html')


@APP.route('/AWS/cfttemplate', methods=['GET'])
def automicheattemplateaws():
    """heat template landing page"""
    return render_template('/AWS/cloudformationtemplate.html')


@APP.route('/AWS/package', methods=['GET'])
def automicpackageaws():
    """download package"""
    return render_template('/AWS/package.html')


@APP.route('/static/bootstrap-archive.zip', methods=['GET', 'POST'])
def downloadaws():
    """download link"""
    return send_from_directory(APP.static_folder, filename='bootstrap-archive.zip')


"""Openstack flow"""


@APP.route('/Openstack/initcfg', methods=['GET'])
def automicinitcfg():
    """Init-config file"""
    return render_template('Openstack/initcfg.html')


@APP.route('/Openstack/init', methods=['POST'])
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

        return redirect('/Openstack/bootstrap')

    return render_template('/Openstack/bootstrap.html')


@APP.route('/Openstack/bootstrap', methods=['GET'])
def automicbootstrap():
    """bootstrap landing page"""
    return render_template('Openstack/bootstrap.html')


@APP.route('/Openstack/bootstrap', methods=['POST'])
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

        return redirect('/Openstack/license')
    return render_template('/Openstack/license.html')


@APP.route('/Openstack/license', methods=['GET'])
def automiclicense():
    """license landing page"""
    return render_template('/Openstack/license.html')


@APP.route('/Openstack/lic', methods=['POST'])
def automiclic():
    """license form values"""
    form = LICENSE(request)

    if request.method == 'POST':

        with open(AUTH_CODE, 'w') as ini:
            ini.write(form.li)
            ini.flush()
        return redirect('/Openstack/heattemplate')
    return render_template('/Openstack/heat.html')


@APP.route('/Openstack/heat', methods=['POST'])
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

        return redirect('/Openstack/package')
    return render_template('Openstack/package.html')


@APP.route('/Openstack/heattemplate', methods=['GET'])
def automicheattemplate():
    """heat template landing page"""
    return render_template('/Openstack/heat.html')


@APP.route('/Openstack/package', methods=['GET'])
def automicpackage():
    """download package"""
    return render_template('Openstack/package.html')


@APP.route('/static/bootstrap-archive.zip', methods=['GET', 'POST'])
def download():
    """download link"""
    return send_from_directory(APP.static_folder, filename='bootstrap-archive.zip')


"""ONAP workflow"""


@APP.route('/ONAP/initcfg', methods=['GET'])
def automicinitcfgopenecomp():
    """ONAP initcfg page"""
    return render_template('/ONAP/initcfg.html')


@APP.route('/ONAP/init', methods=['POST'])
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

        return redirect('/ONAP/bootstrap')

    return render_template('/ONAP/bootstrap.html')


@APP.route('/ONAP/bootstrap', methods=['GET'])
def automicbootstrapopenecomp():
    """onap bootstrap landing page"""
    return render_template('/ONAP/bootstrap.html')


@APP.route('/ONAP/boot', methods=['POST'])
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

        return redirect('/ONAP/license')
    return render_template('/ONAP/license.html')


@APP.route('/ONAP/license', methods=['GET'])
def automiclicenseopenecomp():
    """onap license landing page"""
    return render_template('/ONAP/license.html')


@APP.route('/ONAP/lic', methods=['POST'])
def automiclicopenecomp():
    """onap license form values"""

    form = LICENSE(request)

    if request.method == 'POST':

        with open(AUTH_CODE_ONAP_OUT, 'w') as ini:
            ini.write(form.li)
            ini.flush()
        return redirect('/ONAP/heattemplate')
    return render_template('/ONAP/heat.html')


@APP.route('/ONAP/heattemplate', methods=['GET'])
def automicheattemplateopenecomp():
    """onap heat template landing page"""
    return render_template('/ONAP/heat.html')


@APP.route('/ONAP/heat', methods=['POST'])
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

        return redirect('/ONAP/package')
    return render_template('/ONAP/package.html')


@APP.route('/ONAP/package', methods=['GET'])
def automicpackageopenecomp():
    """onap download package"""
    return render_template('/ONAP/package.html')


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


"""Deploy Workflow"""


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


"""Connectors"""


@APP.route('/connector/nuage/', methods=['GET'])
def automicconnectornuage():
    """Nuage connector landing page"""
    return render_template('/connector/nuage/automicinit.html')


@APP.route('/connector/openstack/', methods=['GET'])
def automicconnectoropenstack():
    """Openstack connector landing page"""
    return render_template('/connector/openstack/automicinit.html')


"""JUJU"""


@APP.route('/juju', methods=['GET'])
def juju():
    """redirection to JUJU_GUI website"""
    return redirect(JU_JU)


if __name__ == "__main__":
    APP.secret_key = os.urandom(12)
    APP.run(host=HOST_ADDRESS, port=HOST_PORT, debug=True)
