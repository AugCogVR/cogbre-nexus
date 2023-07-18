from flask import Flask, request #, jsonify
from flask_restful import Resource, Api #, reqparse
#import pandas as pd
#import ast
import random
import string
import json
import os
import sys
import argparse
from canned_oxide_program import *
from compviz import *
from session import *


app = Flask(__name__)
api = Api(app)

# Import Oxide if Oxide path is given
parser = argparse.ArgumentParser('cogbre nexus API server')
parser.add_argument("--oxidepath", type=str, help="Path to active Oxide installation.", required=False)
args = parser.parse_args()
useOxide = not(args.oxidepath is None)
if (useOxide):
    print(args.oxidepath)
    sys.path.append(args.oxidepath)
    from core import oxide as local_oxide
    print(local_oxide.collection_names())
# TODO: catch error and set useOxide = False

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

        elif (commandList[0] == "get_canned_oxide_program"):
            oxideProgram = CannedOxideProgram(os.path.join(cannedOxideProgramsLocation, commandList[1]))
            responseString = oxideProgram.getBlocksJson()

        elif (commandList[0] == "get_compviz_stages"):
            compVizStages = CompVizStages(os.path.join(compVizProgramsLocation, commandList[1]), commandList[1])
            responseString = compVizStages.getStagesJson()
       
        elif (commandList[0] == "oxide_collection_names"):
            responseString = "OXIDE NOT IN USE"
            if (useOxide):
                responseString = str(local_oxide.collection_names()).replace("'", '"')

        elif (commandList[0] == "oxide_get_cid_from_name"):
            responseString = "OXIDE NOT IN USE"
            if (useOxide):
                responseString = '"' + str(local_oxide.get_cid_from_name(commandList[1])) + '"'

        elif (commandList[0] == "oxide_get_collection_info"):
            responseString = "OXIDE NOT IN USE"
            if (useOxide):
                responseString = str(local_oxide.get_collection_info(commandList[1], commandList[2])).replace("'", '"')

        return responseString, 200  # return repsonse and 200 OK code


sessionControllers = []
cannedOxideProgramsLocation = os.path.join("data", "samples", "bre")
compVizProgramsLocation = os.path.join("data", "samples", "compviz")

api.add_resource(SyncPortal, "/sync_portal")  # the primary/only entry point -- not following API best practices of one resource/entry point per function

if __name__ == "__main__":
    
    sessionControllers = SessionControllers()

    app.run()  # run our Flask app

