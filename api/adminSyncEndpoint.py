from flask import request 
from flask_restful import Resource
import json

# Class defining the API endpoint for syncing with the Nexus GUI
class AdminSyncEndpoint(Resource):
    def __init__(self, **kwargs):
        self.userSessions = kwargs["userSessions"]

    def post(self):
        content = request.get_json(force = True)
        commandList = content["command"]
        responseString = f"Command not processed: {commandList}"

        # Report the command received, unless it's a very frequent activity update
        if (commandList[0] == "get_telemetry"):
            print("!", end="")
        else:
            print(f"ADMIN POSTED: command = {content['command']}")

        if (commandList[0] == "get_active_user_list"):
            responseObject = []
            for userSession in list(self.userSessions.userSessions.values()):
                if (userSession.isActive):
                    responseObject.append({"id" : userSession.userId, "name" : userSession.userName})
            return json.dumps(responseObject), 200

        elif (commandList[0] == "get_config"):
            userId = commandList[1]
            responseObject = {}
            if (userId in self.userSessions.userSessions):
                userSession = self.userSessions.getUserSession(userId)
                if (userSession.isActive):
                    responseObject["stuff"] = "stuff2"
            return json.dumps(responseObject), 200

        elif (commandList[0] == "set_config"):
            userId = commandList[1]
            newConfig = commandList[2]
            print("GOT NEW CONFIG: ", newConfig)
            if (userId in self.userSessions.userSessions):
                userSession = self.userSessions.getUserSession(userId)
                if (userSession.isActive):
                    userSession.sessionConfigDirty = True
            responseObject = {}
            return json.dumps(responseObject), 200

        elif (commandList[0] == "get_telemetry"):
            userId = commandList[1]
            responseObject = []
            if (userId in self.userSessions.userSessions):
                userSession = self.userSessions.getUserSession(userId)
                if (userSession.isActive):
                    for sessionObject in list(userSession.sessionObjects.values()):
                        responseObject.append({"id":sessionObject.objectId, "time":f"{(sessionObject.lastUpdateTime - sessionObject.startTime):0.2f}s"})
                        # responseString += f"{sessionObject.objectId} {(sessionObject.lastUpdateTime - sessionObject.startTime):0.2f}s {float(sessionObject.x):0.2f} {float(sessionObject.y):0.2f} {float(sessionObject.z):0.2f} | "
            return json.dumps(responseObject), 200

        # If we get here, there is an error.
        return json.dumps(responseString), 500  

