import os
from flask import Flask, render_template, redirect, flash, url_for, request, session, send_from_directory
from shutil import make_archive
import logging

import pdb
import shutil
app = Flask(__name__, static_folder='static')


@app.route('/login', methods=['POST', 'GET'])
def do_admin_login():
    if request.form['username'] == 'admin' and request.form['password'] == 'automic123!':
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
        with open('init-cfg.txt', 'w') as ini:
            ini.write(initcfg1)
            ini.flush()
    return btstrap

@app.route('/automic', methods=['GET'])
def automic():
    return render_template('automicexplosion.html')

#@app.route('/automic1', methods=['POST'])
#def automic1():
#    #    pdb.set_trace()
#    mgti = request.form["mgtip"]
#    mgtm = request.form['mgtmask']
#    mgtg = request.form['mgtgateway']
#    mgtd = request.form['mgtdns']
#    e1i = request.form['e1ip']
#    e1z = request.form['e1zone']
#    e1int = request.form['e1inttype']
#    e1p = request.form['e1profile']
#    e2i = request.form['e2ip']
#    e2z = request.form['e2zone']
#    e2int = request.form['e2inttype']
#    e2p = request.form['e2profile']
#    dfrd = request.form['dfrdest']
#    dfri = request.form['dfrint']
#    aout = request.form['AllowOut']

#    if request.method == 'POST':
#        with open('init-cfg.txt', 'w') as automic_initcfg:
#            automic_initcfg.write(str('mgti', 'mgtm', 'mgtg', 'mgtd'))
#            automic_initcfg.flush()
#        print(request.form)
#        print(mgtd)
#        print(mgti)
#        print("%s" % mgti)
#        with open('init-cfg.txt', 'w') as ini:
#            ini.write(mgti)
#            ini.flush()
#        return redirect('/automic')
#    else:
#    return render_template('automic.html')

@app.route('/automicinitcfg', methods=['GET'])
def automicinitcfg():
    return render_template('automicexplosioninit.html')

@app.route('/KVM/automicinitcfg', methods=['GET'])
def automicinitcfgkvm():
    return render_template('automicexplosioninit.html')
@app.route('/Openstack/automicinitcfg', methods=['GET'])
def automicinitcfgopenstack():
    return render_template('automicexplosioninit.html')
@app.route('/ESXi/automicinitcfg', methods=['GET'])
def automicinitcfgesxi():
    return render_template('automicexplosioninit.html')
@app.route('/azure/automicinitcfg', methods=['GET'])
def automicinitcfgazure():
    return render_template('automicexplosioninit.html')
@app.route('/AWS/automicinitcfg', methods=['GET'])
def automicinitcfgaws():
    return render_template('automicexplosioninit.html')


@app.route('/automicinit', methods=['POST'])
def automicinit():
    initi = request.form.to_dict()
    mgti = request.form["mgtip"]
    mgtm = request.form['mgtmask']
    mgtg = request.form['mgtgateway']
    mgtd = request.form['mgtdns']
    hstnme = request.form['hstnme']
    if request.method == 'POST':
        print(initi)
        print(request.form)
        print(mgti)
        print("%s" % mgti)

        with open('init-cfg.txt') as infile, open('static/bootstrap/config/init-cfg.txt', 'w') as outfile:
            for line in infile:
                for src, target in initi.items():
                    line = line.replace(src, target)
                outfile.write(line)

        return redirect('/automicbootstrap')

    return render_template('automicboot.html')

@app.route('/automicbootstrap', methods=['GET'])
def automicbootstrap():
    return render_template('automicexplosionboot.html')

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

        with open('bootstrap1.xml') as infile, open('static/bootstrap/config/bootstrap.xml', 'w') as outfile:
            for line in infile:
                for src, target in booti.items():
                    line = line.replace(src, target)
                outfile.write(line)

        return redirect('/automiclicense')
#    else:
    return render_template('automiclic.html')

@app.route('/automiclicense', methods=['GET'])
def automiclicense():
    return render_template('automicexplosionlic.html')

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

@app.route('/automicheattemplate', methods=['GET'])
def automicheattemplate():
    return render_template('automicexplosionheat.html')

@app.route('/automicheat', methods=['POST'])
def automicheat():
#    pdb.set_trace()
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

        with open('heat-environment1.yaml') as infile, open('static/bootstrap/heat-environment.yaml', 'w') as outfile:
            for line in infile:
                for src, target in heati.items():
                    line = line.replace(src, target)
                outfile.write(line)
        archive_name = os.path.expanduser(os.path.join('~', 'PycharmProjects/untitled/static/bootstrap-archive'))
        root_dir = os.path.expanduser(os.path.join('~', 'PycharmProjects/untitled/static/bootstrap'))
        make_archive(archive_name, 'zip', root_dir)

        return redirect('/automicpackage')
#    else:
    return render_template('automicexplosionpkg.html')

@app.route('/automicpackage', methods=['GET'])
def automicpackage():

    return render_template('automicexplosionpkg.html')

#@app.route('/automicpkg', methods=['GET', 'POST'])
#def automicpkg():
    #    pdb.set_trace()

#    return render_template('automicexplosionpkg.html')
@app.route('/static/bootstrap-archive.zip', methods=['GET', 'POST'])
def download():
    return send_from_directory(app.static_folder, filename='bootstrap-archive.zip')

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(host='0.0.0.0', port=8080, debug=True)
