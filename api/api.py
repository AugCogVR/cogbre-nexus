from flask import Flask, request #, jsonify
from flask_restful import Resource, Api #, reqparse
#import pandas as pd
#import ast
import random
import string
import json
import os
from oxide_program import OxideProgram
from session import *


app = Flask(__name__)
api = Api(app)


class SyncPortal(Resource):
    def post(self):
        content = request.get_json(force = True)
        print(f"POSTED: userId = {content['userId']} command = {content['command']}")

        responseString = "command not processed: " + content["command"]

        commandList = content["command"].split()

        if (commandList[0] == "session_init"):
            sessionController = SessionController(content["userId"])
            sessionControllers.addSessionController(sessionController)
            responseString = "session initialized for user " + content["userId"]

        elif (commandList[0] == "get_session_update"):
            responseString = "session update requested for user " + content["userId"]

        elif (commandList[0] == "get_oxide_program"):
            oxideprogram = OxideProgram(os.path.join(oxideProgramsLocation, commandList[1]))
            responseString = oxideprogram.getBlocksJson()
       

        return responseString, 200  # return repsonse and 200 OK code


sessionControllers = []
oxideProgramsLocation = os.path.join("data", "samples", "bre")

api.add_resource(SyncPortal, "/sync_portal")  # entry point

if __name__ == "__main__":
    
    sessionControllers = SessionControllers()

    app.run()  # run our Flask app

