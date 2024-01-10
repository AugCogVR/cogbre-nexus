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


# TODO: REALLY WANT TO REMOVE THIS CANNED STUFF but not until front-end pieces that use it are updated to use live data.
# cannedOxideProgramsLocation = os.path.join("data", "samples", "bre")
# compVizProgramsLocation = os.path.join("data", "samples", "compviz")


# Import Oxide if Oxide path is given
parser = argparse.ArgumentParser('cogbre nexus API server')
parser.add_argument("--oxidepath", type=str, help="Path to active Oxide installation.", required=False)
args = parser.parse_args()
useOxide = not(args.oxidepath is None)
if (useOxide):
    print(f'oxide path: {args.oxidepath}')
    # We assume the user gave the home directory for Oxide. 
    sys.path.append(args.oxidepath+'/src')
    sys.path.append(args.oxidepath+'/src/oxide')
    from oxide.core import oxide as local_oxide
#    print(local_oxide.collection_names())
# TODO: catch errors and set useOxide = False


class SyncPortal(Resource):
    def post(self):
        content = request.get_json(force = True)
        print(f"POSTED: userId = {content['userId']} command = {content['command']}")
        commandList = content["command"]
        responseString = f"Command not processed: {commandList}"
        if ("oxide" in commandList[0]):
            responseString += " ... is oxidepath specified?"

        if (commandList[0] == "session_init"):
            sessionController = SessionController(content["userId"])
            sessionControllers.addSessionController(sessionController)
            responseString = "session initialized for user " + content["userId"]
            return json.dumps(responseString), 200

        elif (commandList[0] == "get_session_update"):
            responseString = "session update requested for user " + content["userId"]
            return json.dumps(responseString), 200

        # COMMENTED OUT BECAUSE I INTEND TO REMOVE THIS SOON! 
        # Supply canned or semi-canned info for initatives that are dormant -- comment it out for now. 
        # elif (commandList[0] == "get_canned_oxide_program"):
        #     oxideProgram = CannedOxideProgram(os.path.join(cannedOxideProgramsLocation, commandList[1]))
        #     return oxideProgram.getBlocksJson(), 200

        # COMMENTED OUT BECAUSE I INTEND TO REMOVE THIS SOON! 
        # Supply canned or semi-canned info for initatives that are dormant -- comment it out for now. 
        # elif (commandList[0] == "get_compviz_stages"):
        #     compVizStages = CompVizStages(os.path.join(compVizProgramsLocation, commandList[1]), commandList[1])
        #     return compVizStages.getStagesJson(), 200

        elif (useOxide):

            if (commandList[0] == "oxide_collection_names"):
                responseObject = local_oxide.collection_names()
                return json.dumps(responseObject), 200

            elif (commandList[0] == "oxide_get_cid_from_name"):
                colName = commandList[1]
                responseObject = local_oxide.get_cid_from_name(colName)
                return json.dumps(responseObject), 200

            elif (commandList[0] == "oxide_get_collection_info"):
                colName = commandList[1]
                view = commandList[2]
                responseObject = local_oxide.get_collection_info(colName, view)
                return json.dumps(responseObject), 200

            # Find all OIDs with a given name. NOTE: Nothing uses this. 
            elif (commandList[0] == "oxide_get_oids_with_name"):
                someName = commandList[1]
                responseObject = local_oxide.get_oids_with_name(someName)
                return json.dumps(responseObject), 200

            # Get all the Object IDs associated with a Collection ID
            # NOTE: This function does not directly map to an Oxide API function.
            # It is included for convenience. 
            # Perhaps I should implement a wrapper for get_field instead. 
            elif (commandList[0] == "oxide_get_oids_with_cid"):
                someCid = commandList[1]
                responseObject = local_oxide.get_field("collections", someCid, "oid_list")
                return json.dumps(responseObject), 200

            # Get a list of available modules in a category. NOTE: Nothing uses this. 
            elif (commandList[0] == "oxide_get_available_modules"):
                category = commandList[1]
                responseObject = local_oxide.get_available_modules(category)
                return json.dumps(responseObject), 200

            # This command alters the output of the documentation function
            # because some values are not serializable.
            # Only return "description" and "Usage" (if available) 
            elif (commandList[0] == "oxide_documentation"):
                moduleName = commandList[1]
                responseObject = local_oxide.documentation(moduleName)
                newDict = { "description" : responseObject["description"] }
                if ("Usage" in responseObject):
                    newDict["Usage"] = responseObject["Usage"]
                return json.dumps(newDict), 200

            # Return names associated with provided OID
            elif (commandList[0] == "oxide_get_names_from_oid"):
                OID = commandList[1]
                # Formats the set of names into a string before dumping to json
                responseObject = list(local_oxide.get_names_from_oid(OID))
                return json.dumps(responseObject), 200

            # Get file size of a binary file represented by the given OID
            elif (commandList[0] == "oxide_get_oid_file_size"):
                OID = commandList[1]
                responseObject = local_oxide.get_field("file_meta", OID, "size")
                return json.dumps(responseObject), 200

            # Call any module with the supplied parameters and return the results
            elif (commandList[0] == "oxide_retrieve"):
                moduleName = commandList[1]
                oidList = commandList[2]
                opts = commandList[3]
                responseObject = local_oxide.retrieve(moduleName, oidList, opts)
                return json.dumps(responseObject), 200

            # Use disassembly module to get disassembly with default fields (see alternatives below)
            # This command alters the output of the disassembly module to simplify it because 
            # every client-side (C#) JSON parser that I tried barfs on the nested arrays
            # (C# default, NewtonSoft, LitJson)
            elif (commandList[0] == "oxide_get_disassembly"):
                OID = commandList[1] 
                responseObject = local_oxide.retrieve("disassembly", [ OID ])
                # We'll create a custom response object with just the info we want
                customResponseObject = {}
                # Walk through each oid, gather certain data, and add it to custom repsonse object
                for oid, oidInfo in responseObject.items():
                    customOidInfo = {}
                    customOidInfo["instructions"] = {}
                    for offset, instructionDict in oidInfo["instructions"].items(): 
                        customInstructionDict = {}
                        customInstructionDict["mnemonic"] = instructionDict["mnemonic"]
                        customInstructionDict["op_str"] = instructionDict["op_str"]
                        customInstructionDict["str"] = instructionDict["str"]
                        customOidInfo["instructions"][offset] = customInstructionDict
                    customResponseObject[oid] = customOidInfo
                return json.dumps(customResponseObject), 200

            # Use basic_blocks module to grab basic blocks of a binary.
            # This command alters the output of the basic_blocks module to simplify it because 
            # every client-side (C#) JSON parser that I tried barfs on the nested arrays
            # (C# default, NewtonSoft, LitJson)
            elif (commandList[0] == "oxide_get_basic_blocks"):
                OID = commandList[1] 
                responseObject = local_oxide.retrieve("basic_blocks", [ OID ])
                # We'll create a custom response object with just the info we want
                customResponseObject = {}
                # Walk through each oid, gather certain data, and add it to custom repsonse object
                for oid, oidInfo in responseObject.items():
                    customOidInfo = {}
                    for insn, blockInfo in oidInfo.items():
                        customBlockInfo = {}
                        memberList = []
                        for member in blockInfo["members"]:
                            memberList.append(f"{member[0]}")
                        customBlockInfo["members"] = memberList
                        destList = []
                        for dest in blockInfo["dests"]:
                            destList.append(f"{dest}")
                        customBlockInfo["dests"] = destList
                        customOidInfo[f"{insn}"] = customBlockInfo
                    customResponseObject[oid] = customOidInfo
                return json.dumps(customResponseObject), 200

        return json.dumps(responseString), 500  # if we get here, there is an error


sessionControllers = []
api.add_resource(SyncPortal, "/sync_portal")  # the primary/only entry point -- not following API best practices of one resource/entry point per function
if __name__ == "__main__":
    sessionControllers = SessionControllers()
    app.run()  # run our Flask app

