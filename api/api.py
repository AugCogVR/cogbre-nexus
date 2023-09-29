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
import shlex
from canned_oxide_program import *
from compviz import *
from session import *


app = Flask(__name__)
api = Api(app)

cannedOxideProgramsLocation = os.path.join("data", "samples", "bre")
compVizProgramsLocation = os.path.join("data", "samples", "compviz")

# Import Oxide if Oxide path is given
parser = argparse.ArgumentParser('cogbre nexus API server')
parser.add_argument("--oxidepath", type=str, help="Path to active Oxide installation.", required=False)
args = parser.parse_args()
useOxide = not(args.oxidepath is None)
if (useOxide):
    print(args.oxidepath)
    sys.path.append(args.oxidepath)
    from core import oxide as local_oxide
#    print(local_oxide.collection_names())
# TODO: catch errors and set useOxide = False


class SyncPortal(Resource):
    def post(self):
        content = request.get_json(force = True)
        print(f"POSTED: userId = {content['userId']} command = {content['command']}")
        commandList = content["command"]
        responseString = f"Command not processed: {commandList}"

        if (commandList[0] == "session_init"):
            sessionController = SessionController(content["userId"])
            sessionControllers.addSessionController(sessionController)
            responseString = "session initialized for user " + content["userId"]
            return json.dumps(responseString), 200

        elif (commandList[0] == "get_session_update"):
            responseString = "session update requested for user " + content["userId"]
            return json.dumps(responseString), 200

        elif (commandList[0] == "get_canned_oxide_program"):
            oxideProgram = CannedOxideProgram(os.path.join(cannedOxideProgramsLocation, commandList[1]))
            return oxideProgram.getBlocksJson(), 200

        elif (commandList[0] == "get_compviz_stages"):
            compVizStages = CompVizStages(os.path.join(compVizProgramsLocation, commandList[1]), commandList[1])
            return compVizStages.getStagesJson(), 200
       
        elif (commandList[0] == "oxide_collection_names"):
            responseString += " !!! OXIDE NOT IN USE"
            if (useOxide):
                responseString = local_oxide.collection_names()
                return json.dumps(responseString), 200

        elif (commandList[0] == "oxide_get_cid_from_name"):
            responseString += " !!! OXIDE NOT IN USE"
            if (useOxide):
                colName = commandList[1]
                responseString = local_oxide.get_cid_from_name(colName)
                return json.dumps(responseString), 200

        elif (commandList[0] == "oxide_get_collection_info"):
            responseString += " !!! OXIDE NOT IN USE"
            if (useOxide):
                colName = commandList[1]
                view = commandList[2]
                responseString = local_oxide.get_collection_info(colName, view)
                return json.dumps(responseString), 200

        elif (commandList[0] == "oxide_get_file_info"):
            responseString += " !!! OXIDE NOT IN USE"
            if (useOxide):
                fileName = commandList[1]
                responseString = local_oxide.get_file_info(fileName)
                return json.dumps(responseString), 200

        elif (commandList[0] == "oxide_get_oids_with_name"):
            responseString += " !!! OXIDE NOT IN USE"
            if (useOxide):
                someName = commandList[1]
                responseString = local_oxide.get_oids_with_name(someName)
                return json.dumps(responseString), 200

        # NOTE: This function does not directly map to an Oxide API function.
        # It is included for convenients. 
        # Perhaps I should implement a wrapper for get_field instead. 
        elif (commandList[0] == "oxide_get_oids_with_cid"):
            responseString += " !!! OXIDE NOT IN USE"
            if (useOxide):
                someCid = commandList[1]
                responseString = local_oxide.get_field("collections", someCid, "oid_list")
                return json.dumps(responseString), 200

        elif (commandList[0] == "oxide_get_available_modules"):
            responseString += " !!! OXIDE NOT IN USE"
            if (useOxide):
                category = commandList[1]
                responseString = local_oxide.get_available_modules(category)
                return json.dumps(responseString), 200

        elif (commandList[0] == "oxide_documentation"):
            responseString += " !!! OXIDE NOT IN USE"
            if (useOxide):
                moduleName = commandList[1]
                response = local_oxide.documentation(moduleName)
                newDict = { "description" : response["description"] }
                if ("Usage" in response):
                    newDict["Usage"] = response["Usage"]
                return json.dumps(newDict), 200
            # Only return "description" and "Usage" (if available) because "opts_doc" 
            # may contain unserializable types

        elif (commandList[0] == "oxide_get_mod_type"):
            responseString += " !!! OXIDE NOT IN USE"
            if (useOxide):
                moduleName = commandList[1]
                responseString = local_oxide.get_mod_type(moduleName)
                return json.dumps(responseString), 200

        elif (commandList[0] == "oxide_single_call_module"):
            responseString += " !!! OXIDE NOT IN USE"
            if (useOxide):
                moduleType = commandList[1]
                moduleName = commandList[2]
                oidList = commandList[3]
                opts = commandList[4]
                responseString = local_oxide.single_call_module(moduleType, moduleName, oidList, opts)
                return json.dumps(responseString), 200

        return json.dumps(responseString), 500  # if we get here, there is an error


sessionControllers = []
api.add_resource(SyncPortal, "/sync_portal")  # the primary/only entry point -- not following API best practices of one resource/entry point per function
if __name__ == "__main__":
    sessionControllers = SessionControllers()
    app.run()  # run our Flask app

