from flask import Flask, request #, jsonify
from flask_restful import Resource, Api #, reqparse
#import pandas as pd
#import ast
import random
import string
import json
from oxide_program import OxideProgram
from session import *


app = Flask(__name__)
api = Api(app)


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
    program = OxideProgram('../data/samples/bre/elf_fib_recursive')
    sessionControllers = SessionControllers()

    app.run()  # run our Flask app

