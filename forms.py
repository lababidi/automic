"""This module contains the forms for each part of the bootstrap process"""
from flask import request


class INITCFG(object):
    """initcfg form values"""
    def __init__(self, request):
        self.initi = request.form.to_dict()
        self.mgti = request.form["mgtip"]
        self.mgtm = request.form['mgtmask']
        self.mgtg = request.form['mgtgateway']
        self.mgtd = request.form['mgtdns']
        self.hstnme = request.form['hstnme']
        self.pno = request.form['pno']
        self.panokey = request.form['panokey']


class BOOTSTRAP(object):
    """bootstrap form values"""
    def __init__(self, request):
        self.booti = request.form.to_dict()
        self.e1i = request.form['e1ip']
        self.e1z = request.form['e1zone']
        self.e1int = request.form['e1inttype']
        self.e1p = request.form['e1profile']
        self.e2i = request.form['e2ip']
        self.e2z = request.form['e2zone']
        self.e2int = request.form['e2inttype']
        self.e2p = request.form['e2profile']
        self.dfrd = request.form['dfrdest']
        self.dfri = request.form['dfrint']
        self.dfrnh = request.form['dfrnh']
        self.aout = request.form['AllowOut']


class LICENSE(object):
    """license form values"""
    def __init__(self, request):
        self.li = request.form["lic"]

class HEAT(object):
    """heat template form values"""
    def __init__(self, request):
        self.heati = request.form.to_dict()
        self.oi = request.form['oin']
        self.ofb = request.form['ofl']
        self.omn = request.form['omnn']
        self.oms = request.form['omsn']
        self.omi = request.form['omip']
        self.osn = request.form['osnn']
        self.oss = request.form['ossn']
        self.ooi = request.form['ooip']
        self.oin = request.form['oisn']
        self.ois = request.form['oiss']
        self.oii = request.form['oiip']


class ONAPHEAT(object):
    """onap heat template form values"""
    def __init__(self, request):
        self.heati = request.form.to_dict()
        self.oi = request.form['oin']
        self.ofb = request.form['ofl']
        self.omn = request.form['omnn']
        self.oms = request.form['omsn']
        self.omi = request.form['omip']
        self.osn = request.form['osnn']
        self.oss = request.form['ossn']
        self.ooi = request.form['ooip']
        self.oin = request.form['oisn']
        self.ois = request.form['oiss']
        self.oii = request.form['oiip']


class DEPLOY(object):
    """deploy form values"""
    def __init__(self, request):
        self.initi = request.form.to_dict()
        self.authurl = request.form["authurl"]
        self.usr = request.form['usr']
        self.tenantnme = request.form['tenantnme']
        self.ospasswd = request.form['ospasswd']
        self.hstnme = request.form['hstnme']
        self.cntl1 = request.form['cntl1']


class ADDMACHINE(object):
    """add instance to be deployed"""
    def __init__(self, request):
        self.json_data = request.json['info']
        self.devicename = json_data['device']
        self.ipaddress = json_data['ip']
        self.username = json_data['username']
        self.password = json_data['password']
        self.portnumber = json_data['port']


class updatemachine(object):
    """update instance"""
    def __init__(self, request):
        self.machineinfo = request.json['info']
        self.machineid = machineinfo['id']
        self.device = machineinfo['device']
        self.ip = machineinfo['ip']
        self.username = machineinfo['username']
        self.password = machineinfo['password']
        self.port = machineinfo['port']


class EXECUTE(object):
    """run command on instance"""
    def __init__(self, request):
        self.machineinfo = request.json['info']
        self.ip = machineinfo['ip']
        self.username = machineinfo['username']
        self.password = machineinfo['password']
        self.command = machineinfo['command']
        self.isroot = machineinfo['isroot']




