# -*- coding: utf-8 -*-
from flask import Flask, request, render_template, jsonify, json
from flask_restful import Api, Resource, abort
from pymongo import MongoClient
import json
from bson.objectid import ObjectId
from fabric.api import *

# Create Flask app
app = Flask(__name__)


client = MongoClient('localhost:27017')
db = client.MachineData

# Display the homepage
@app.route('/')
def index():
    return app.send_static_file('index.html')

# Create RESTful API
api = Api(app, prefix="/rest")

# This is our small in-memory database with some
# simple collections of objects
Meta = {"curr_student_id" : 1}
Students = [{"name" : "Eric Zhu",
             "id" : 1,
             "grade" : 86},]

# Collection resource
class StudentsResource(Resource):
    
    def get(self):
        return Students

    def post(self):
        new_student = request.json
        student_id = new_student['id']
        select = [s for s in Students if s['id'] == student_id]
        if len(select) == 1:
            # if the student already exist, apply updates
            select[0] = new_student
        elif len(select) == 0:
            # if not exist before, add new
            Students.append(new_student)
        else:
            # we get error
            abort(500)
        return {'status' : 'acknowledged'}, 201

    def delete(self, student_id):
        Students[:] = [s for s in Students if s['id'] != student_id]
        return {'status' : 'acknowledged'}, 204

api.add_resource(StudentsResource, '/students',
                                    '/students/<int:student_id>')


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

if __name__ == '__main__':
    app.run(debug=True)