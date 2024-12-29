from flask import request 
from flask_restful import Resource
import json

# Class defining the API endpoint for syncing with clients (e.g., VR clients)
class ClientSyncEndpoint(Resource):
    def __init__(self, **kwargs):
        self.userSessions = kwargs["userSessions"]
        self.local_oxide = kwargs["local_oxide"]
        self.capaRulesPath = kwargs["capaRulesPath"]

    def post(self):
        content = request.get_json(force = True)
        sessionId = content["sessionId"]
        commandList = content["command"]

        # Report the command received, unless it's a very frequent activity update
        if (commandList[0] == "session_update"):
            print(".", end="", flush=True)
        else:
            print(f"CLIENT POSTED: sessionId = {content['sessionId']} command = {content['command']}")

        # Set default response string for failure. Successful command execution will
        # overwrite it. 
        responseString = f"Command not processed: {commandList}"
        if ("oxide" in commandList[0]):
            responseString += " ... is oxidepath correct?"

        if (commandList[0] == "session_init"):
            responseObject = {}
            self.userSessions.openUserSession(sessionId)
            userSession = self.userSessions.getUserSession(sessionId)

            # TEMPORARILY turn on logging by default for debugging purposes
            if ((userSession is not None) and (userSession.isActive)):
                userSession.startLogging()
                print("TELEMMETRY LOGGING STARTED")

            userSession.sessionConfig = commandList[1]
            # print("CONFIG DATA: ", commandList[1])
            return json.dumps(responseObject), 200

        elif (commandList[0] == "session_update"):
            responseObject = {}
            userSession = self.userSessions.getUserSession(sessionId)
            userSession.updateUserSession(commandList)
            if (userSession.sessionConfigDirty):
                userSession.sessionConfigDirty = False
                responseObject["config_update"] = userSession.sessionConfig
            return json.dumps(responseObject), 200

        elif (commandList[0] == "oxide_collection_names"):
            responseObject = self.local_oxide.collection_names()
            return json.dumps(responseObject), 200

        elif (commandList[0] == "oxide_get_cid_from_name"):
            colName = commandList[1]
            responseObject = self.local_oxide.get_cid_from_name(colName)
            return json.dumps(responseObject), 200

        elif (commandList[0] == "oxide_get_collection_info"):
            colName = commandList[1]
            view = commandList[2]
            responseObject = self.local_oxide.get_collection_info(colName, view)
            return json.dumps(responseObject), 200

        # Find all OIDs with a given name. NOTE: Nothing uses this. 
        elif (commandList[0] == "oxide_get_oids_with_name"):
            someName = commandList[1]
            responseObject = self.local_oxide.get_oids_with_name(someName)
            return json.dumps(responseObject), 200

        # Get all the Object IDs associated with a Collection ID
        # NOTE: This function does not directly map to an Oxide API function.
        # It is included for convenience. 
        # Perhaps I should implement a wrapper for get_field instead. 
        elif (commandList[0] == "oxide_get_oids_with_cid"):
            someCid = commandList[1]
            responseObject = self.local_oxide.get_field("collections", someCid, "oid_list")
            return json.dumps(responseObject), 200

        # Get a list of available modules in a category. NOTE: Nothing uses this. 
        elif (commandList[0] == "oxide_get_available_modules"):
            category = commandList[1]
            responseObject = self.local_oxide.get_available_modules(category)
            return json.dumps(responseObject), 200

        # This command alters the output of the documentation function
        # because some values are not serializable.
        # Only return "description" and "Usage" (if available) 
        elif (commandList[0] == "oxide_documentation"):
            moduleName = commandList[1]
            responseObject = self.local_oxide.documentation(moduleName)
            newDict = { "description" : responseObject["description"] }
            if ("Usage" in responseObject):
                newDict["Usage"] = responseObject["Usage"]
            return json.dumps(newDict), 200

        # Return names associated with provided OID
        elif (commandList[0] == "oxide_get_names_from_oid"):
            OID = commandList[1]
            # Formats the set of names into a string before dumping to json
            responseObject = list(self.local_oxide.get_names_from_oid(OID))
            return json.dumps(responseObject), 200

        # Get file size of a binary file represented by the given OID
        elif (commandList[0] == "oxide_get_oid_file_size"):
            OID = commandList[1]
            responseObject = self.local_oxide.get_field("file_meta", OID, "size")
            return json.dumps(responseObject), 200

        # Call any module with the supplied parameters and return the results
        elif (commandList[0] == "oxide_retrieve"):
            moduleName = commandList[1]
            oidList = commandList[2]
            opts = commandList[3]
            # SLIGHTLY HACKY: Intercept Capa call and add Capa rules path to opts if not specified by caller
            if (moduleName == "capa_results"):
                if (not ("rules_path" in opts)):
                    opts["rules_path"] = self.capaRulesPath
            responseObject = self.local_oxide.retrieve(moduleName, oidList, opts)
            return json.dumps(responseObject), 200

        # Use disassembly module to get disassembly with default fields (see alternatives below)
        # This command alters the output of the disassembly module to simplify it because 
        # every client-side (C#) JSON parser that I tried barfs on the nested arrays
        # (C# default, NewtonSoft, LitJson)
        elif (commandList[0] == "oxide_get_disassembly"):
            OID = commandList[1] 
            responseObject = self.local_oxide.retrieve("disassembly", [ OID ])
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
            responseObject = self.local_oxide.retrieve("basic_blocks", [ OID ])
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

        # If we get here, there is an error.
        return json.dumps(responseString), 500  

