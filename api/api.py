from flask import Flask, request #, jsonify
from flask_restful import Resource, Api #, reqparse
#import pandas as pd
#import ast
import random
import string
import json


app = Flask(__name__)
api = Api(app)


#============================
# Break out to another file, later

class SessionControllers:
    def __init__(self):
        self.sessionControllers = {}

    def addSessionController(self, sessionController):
        self.sessionControllers[sessionController.userId] = sessionController


class SessionController:
    def __init__(self, userId):
        self.userId = userId





#============================
# Also break out to another file, later

class Program:
    def __init__(self, folder):
        blocks_file = open(folder + '/basic_blocks')
        self.blocks = json.load(blocks_file)
        blocks_file.close()
        
        # print(blocks[0])
        # for i in blocks[0]['basic_blocks']:
        #     print(i)
        #     print(blocks[0]['basic_blocks'][i])

    def getBlocksJson(self):
        return json.dumps(self.blocks)
        

#============================




class SyncPortal(Resource):
    def post(self):
        content = request.get_json(force = True)
        print('POSTED: userId =', content['userId'], 'command =', content['command'])

        responseString = 'command not processed: ' + content['command']

        if (content['command'] == 'session_init'):
            sessionController = SessionController(content['userId'])
            sessionControllers.addSessionController(sessionController)
            responseString = program.getBlocksJson()

        elif (content['command'] == 'get_session_update'):
            responseString = 'session update requested for user ' + content['userId']

        return responseString, 200  # return repsonse and 200 OK code


program = ''
sessionControllers = ''

api.add_resource(SyncPortal, '/sync_portal')  # entry point

if __name__ == '__main__':
    program = Program('../data/samples/elf_fib_recursive')
    sessionControllers = SessionControllers()

    app.run()  # run our Flask app

